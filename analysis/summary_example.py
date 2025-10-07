#!/usr/bin/env python3
"""
Exemple d'utilisation du récapitulatif complet
Run in Lyon Race Data Analysis

Ce script montre comment générer et utiliser le tableau récapitulatif
avec toutes les statistiques intéressantes.
"""

from race_analysis import RaceAnalyzer

def main():
    """Exemple d'utilisation du récapitulatif."""
    print("🏃‍♂️ Initialisation de l'analyseur de course...")
    analyzer = RaceAnalyzer()
    
    print("\n🔥 Génération du récapitulatif complet...")
    
    # Option 1: Affichage formaté dans la console
    analyzer.print_comprehensive_summary()
    
    # Option 2: Récupération du DataFrame pour traitement personnalisé
    print("\n📊 Génération du DataFrame pour analyse personnalisée...")
    summary_df = analyzer.generate_comprehensive_summary()
    
    # Exemple : filtrer seulement les statistiques temporelles
    timing_stats = summary_df[summary_df['Métrique'].str.contains('temps|Temps', case=False, na=False)]
    print("\n⏱️ STATISTIQUES TEMPORELLES UNIQUEMENT:")
    print(timing_stats.to_string(index=False))
    
    # Option 3: Sauvegarde en Excel avec formatage personnalisé
    try:
        analyzer.save_summary_excel("mon_recapitulatif_course.xlsx")
    except:
        print("Note: Installez openpyxl pour la sauvegarde Excel")
    
    # Option 4: Rechercher des statistiques spécifiques
    print("\n🔍 RECHERCHE DE STATISTIQUES SPÉCIFIQUES:")
    
    # Trouver les stats de participation
    participation_stats = summary_df[summary_df['Métrique'].str.contains('Participants|participants', na=False)]
    print("\nSTATISTIQUES DE PARTICIPATION:")
    for _, row in participation_stats.iterrows():
        if row['Métrique'] != '' and not row['Métrique'].startswith('='):
            print(f"• {row['Métrique']}: {row['Valeur']} {row['Détail']}")
    
    # Trouver le podium
    podium_stats = summary_df[summary_df['Métrique'].str.contains('place|Meilleur', na=False)]
    print("\nPODIUM ET RECORDS:")
    for _, row in podium_stats.iterrows():
        if row['Métrique'] != '' and not row['Métrique'].startswith('='):
            print(f"• {row['Métrique']}: {row['Valeur']} {row['Détail']}")
    
    print("\n✅ Exemple terminé!")
    print("Consultez les fichiers générés pour plus de détails.")

if __name__ == "__main__":
    main()