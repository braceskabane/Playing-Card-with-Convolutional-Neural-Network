# Label yang digunakan untuk mengambil dataset
labels = (
        "2_Club", "3_Club", "4_Club", "5_Club", "6_Club", "7_Club", "8_Club", "9_Club", "10_Club", "ace_Club", 
        "J_Club", "Q_Club", "K_Club", "2_Diamond", "3_Diamond", "4_Diamond", "5_Diamond", "6_Diamond", "7_Diamond",
        "8_Diamond", "9_Diamond", "10_Diamond", "ace_Diamond", "J_Diamond", "Q_Diamond", "K_Diamond", "2_Heart", 
        "3_Heart", "4_Heart", "5_Heart", "6_Heart", "7_Heart", "8_Heart", "9_Heart", "10_Heart", "ace_Heart", 
        "J_Heart", "Q_Heart", "K_Heart", "2_Spades", "3_Spades", "4_Spades", "5_Spades", "6_Spades", "7_Spades", 
        "8_Spades", "9_Spades", "10_Spades", "ace_Spades", "J_Spades", "Q_Spades", "K_Spades"
)

# Label yang digunakan untuk menghitung nilai sebuah kartu 
precedence_Club = {
    '2_Club': 2, '3_Club': 3, '4_Club': 4, '5_Club': 5, '6_Club': 6, '7_Club': 7, '8_Club': 8, '9_Club': 9, '10_Club': 10,
    'ace_Club': 14, 'J_Club': 11, 'Q_Club': 12, 'K_Club': 13,
}
precedence_Diamond={
    '2_Diamond': 2, '3_Diamond': 3, '4_Diamond': 4, '5_Diamond': 5, '6_Diamond': 6, '7_Diamond': 7,
    '8_Diamond': 8, '9_Diamond': 9, '10_Diamond': 10, 'ace_Diamond': 14, 'J_Diamond': 11, 'Q_Diamond': 12, 'K_Diamond': 13,
}
precedence_Heart= {
    '2_Heart': 2, '3_Heart': 3, '4_Heart': 4, '5_Heart': 5, '6_Heart': 6, '7_Heart': 7, '8_Heart': 8, '9_Heart': 9,
    '10_Heart': 10, 'ace_Heart': 14, 'J_Heart': 11, 'Q_Heart': 12, 'K_Heart': 13,
}
precedence_Spades={
    '2_Spades': 2, '3_Spades': 3, '4_Spades': 4, '5_Spades': 5, '6_Spades': 6, '7_Spades': 7, '8_Spades': 8, '9_Spades': 9,
    '10_Spades': 10, 'ace_Spades': 14, 'J_Spades': 11, 'Q_Spades': 12, 'K_Spades': 13
}

# Fungsi untuk menampilkan kartu-kartu yang ada pada list
# utils.display_cards(self.player_cards, "Player")
def display_cards(cards, player_type):
    print(f"{player_type} Cards:")
    if not cards:
        print("No cards yet.")
    else:
        for idx, card in enumerate(cards, 1):
            print(f"Card {idx}:")
            #print(f"Image: {card['image']}") # Dalam bentuk array matriks
            print(f"Label: {card['label']}") 
            print("-------------------")


# Fungsi menghitung precedence di setiap list player maupun komputer
def calculate_total_precedence(cards):
    total_precedence = 0
    precedences = [precedence_Club, precedence_Diamond, precedence_Heart, precedence_Spades]
    
    for card in cards:
        shape = card['label']
        for precedence in precedences:
            if shape in precedence:
                total_precedence += precedence[shape]
                break
    
    return total_precedence
