import polars as pl

# Replace 'your_file.csv' with the name of your CSV file
csv_file_path = '/Users/jt/Desktop/place/Magic/game_data/premier/game_data_public.DSK.PremierDraft.csv.gz'
output_file_path = '/Users/jt/Desktop/place/Magic/first_few_rows.csv'

# Read the CSV file
df = pl.scan_csv(csv_file_path)

# Get the first few rows
first_few_rows = df.head(30).collect()

# Write the first few rows to a new CSV file
first_few_rows.write_csv(output_file_path)



def card_wr(card, df):
    # Collect schema names to avoid performance warnings
    column_names = df.collect_schema().names()
    
    # Select relevant columns
    columns = [col for col in column_names if col.startswith(f"opening_hand_{card}") or col.startswith(f"drawn_{card}") or col.startswith(f"tutored_{card}") or col.startswith(f"deck_{card}") or col.startswith(f"sideboard_{card}") or col == "won"]
    df_card = df.select(columns)
    
    # Rename columns
    df_card = df_card.rename({col: col.replace(f"_{card}", "") for col in columns})
    
    # Filter decks that played the card
    df_card = df_card.filter(pl.col("deck") > 0)
    
    # Add stats
    df_card = df_card.with_columns([
        (pl.col("opening_hand") + pl.col("drawn")).alias("game_in_hand"),
        (pl.col("opening_hand") + pl.col("drawn") + pl.col("tutored")).alias("game_seen"),
        (pl.col("deck") - (pl.col("opening_hand") + pl.col("drawn") + pl.col("tutored"))).alias("game_not_seen")
    ])
    
    # Adjust Number of Games Not Seen
    df_card = df_card.with_columns([
        pl.when(pl.col("game_not_seen") < 0).then(0).otherwise(pl.col("game_not_seen")).alias("game_not_seen")
    ])
    
    # Calculate win rates
    df_card = df_card.with_columns([
        (pl.col("opening_hand") * pl.col("won")).alias("opening_hand_win"),
        (pl.col("deck") * pl.col("won")).alias("game_played_win"),
        (pl.col("game_in_hand") * pl.col("won")).alias("game_in_hand_win"),
        (pl.col("game_not_seen") * pl.col("won")).alias("game_not_seen_win")
    ])
    
    # Summarize statistics
    summary = df_card.select([
        pl.lit(card).alias("card"),
        pl.sum("deck").alias("games_played_n"),
        (pl.sum("game_played_win") / pl.sum("deck")).alias("game_played_wr"),
        pl.sum("opening_hand").alias("opening_hand_n"),
        (pl.sum("opening_hand_win") / pl.sum("opening_hand")).alias("opening_hand_wr"),
        pl.sum("game_in_hand").alias("game_in_hand_n"),
        (pl.sum("game_in_hand_win") / pl.sum("game_in_hand")).alias("game_in_hand_wr"),
        pl.sum("game_not_seen").alias("game_not_seen_n"),
        (pl.sum("game_not_seen_win") / pl.sum("game_not_seen")).alias("game_not_seen_wr"),
        (pl.sum("game_in_hand_win") / pl.sum("game_in_hand") - pl.sum("game_not_seen_win") / pl.sum("game_not_seen")).alias("iwd")
    ])
    
    return summary.collect()

card_stats = card_wr("Ragged Playmate", df)

print(card_stats)
print(card_wr)



