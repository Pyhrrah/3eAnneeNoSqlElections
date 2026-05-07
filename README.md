TP sur NEO4J
MATHUREL Bryan 3IABD2


Travailler sur le departement 03

### Labels
Region
Departement
Commune
Candidat
Liste
Nuance
Genre

Relations
Candidat->Commune->Departement->Region
Candidat->Liste
Candidat->Nuance
Liste->Nuance
Genre->Candidat->Commune->Departement->Region

## Transferer dans docker des fichiers csv pour integrer dans neo4j

- `docker cp`
- Doivent être dans le dossier de destination `var/lib/neo4j/import`

```sh
# Lancer le container
docker compose up -d


docker cp .\clean\. neo4j_elections:/var/lib/neo4j/import/

# Vérifier
docker exec -it neo4j_elections ls -ail /var/lib/neo4j/import/

docker exec -it neo4j_elections cypher-shell -u neo4j -p password

```

## Importer dans Neo4j

```cypher
MATCH (n) DETACH DELETE n;

LOAD CSV WITH HEADERS FROM 'file:///clean/03-regions.csv' AS row
CREATE (r:Region {
    code: row.region_code,
    name: row.nom_region
});

LOAD CSV WITH HEADERS FROM 'file:///clean/03-departements.csv' AS row
CREATE (d:Departement {
    code: row.code_departement,
    name: row.nom_departement
})
WITH d, row
    MATCH (r: Region {code: row.code_region})
        CREATE (d)-[:REGION]->(r);


LOAD CSV WITH HEADERS FROM 'file:///clean/03-communes.csv' AS row
CREATE (c:Commune {
    codeINSEE: row.code_commune_INSEE,
    name: row.nom_commune,
    location : point({latitude: toFloat(row.latitude), longitude: toFloat(row.longitude)})
})
WITH c, row
    MATCH (d:Departement {code: row.code_departement})
        CREATE (c)-[:DEPARTEMENT]->(d);


LOAD CSV WITH HEADERS FROM 'file:///clean/03-insee.csv' AS row
MATCH (c:Commune {codeINSEE: row.CODGEO})
SET
    c.population = toInteger(row.Population),
    c.nbFemmes = toInteger(row.`Nb Femme`),
    c.nbHommes = toInteger(row.`Nb Homme`),
    c.nbMineurs = toInteger(row.`Nb Mineurs`),
    c.nbMajeurs = toInteger(row.`Nb Majeurs`),
    c.revenuMoyen = toFloat(row.Moyenne_Revenus_fiscaux),
    c.nbEntreprises = toInteger(row.`Nb Entreprises Secteur Services`) +
                      toInteger(row.`Nb Entreprises Secteur Commerce`) +
                      toInteger(row.`Nb Entreprises Secteur Construction`) +
                      toInteger(row.`Nb Entreprises Secteur Industrie`),
    c.tauxPropriete = toFloat(row.Taux_Propriete);



LOAD CSV WITH HEADERS FROM 'file:///clean/03-candidats.csv' AS row
// Créer le nœud Candidat avec les propriétés du CSV
CREATE (can:Candidat {
    nom: row.`Nom sur le bulletin de vote`,
    prenom: row.`Prénom sur le bulletin de vote`,
    sexe: row.`Sexe`,
    nationalite: row.`Nationalité`
})
// Définir la propriété d'affichage pour Neo4j Browser
SET can.name = can.nom + ' ' + can.prenom
// Créer le nœud Liste avec les propriétés du CSV
WITH can, row
    CREATE (l:Liste {
        numeroPanneau: toInteger(row.`Numéro de panneau`),
        libelleAbrege: row.`Libellé abrégé de liste`,
        libelleComplet: row.`Libellé de la liste`
    })
// Créer la relation entre le candidat et sa liste (tête de liste)
WITH can, l, row
    CREATE (can)-[:TETE_DE]->(l)
// Lier la liste et le candidat à la commune via le code circonscription
WITH can, l, row
    MATCH (c:Commune {codeINSEE: row.`Code circonscription`})
        CREATE (l)-[:CANDIDATE_DANS]->(c)
        CREATE (can)-[:CANDIDAT_DANS]->(c)
// Créer ou récupérer la nuance politique et la lier à la liste, au candidat et à la commune
WITH l, can, c, row
    MERGE (n:Nuance {code: row.`Code nuance de liste`, nom: row.`Nuance de liste`})
        CREATE (l)-[:A_NUANCE]->(n)
        CREATE (can)-[:A_NUANCE]->(n)
        CREATE (c)-[:A_NUANCE]->(n);


// Supprimer les départements sans communes
MATCH (d:Departement)
    WHERE NOT ( (:Commune)-[:BELONGS_TO]->(d) )
    DETACH DELETE d;


// Supprimer les régions sans départements
MATCH (r:Region)
    WHERE NOT ( (:Departement)-[:BELONGS_TO]->(r) )
    DETACH DELETE r;


match (c: Commune {codeINSEE: "03190"})-[r*1..3]-(connected) return c,r,connected;

match (c: Commune {codeINSEE: "03190"})-[r*1..3]-(connected) where all(rel in r where type(rel) <> 'A_NUANCE') return c,r,connected;
 
match (c: Candidat )-[:CANDIDAT_DANS]->(com: Commune) return com.name as Commune, COUNT(c) as nbCandidats order by nbCandidats desc limit 100;

match (c: Candidat )-[:TETE_DE]->(:Liste)-[:A_NUANCE]->(n:Nuance) return n.nom as Nuance, COUNT(c) as nbCandidats order by nbCandidats desc limit 100;

match (c:Candidat)-[r]-(connected) where c.name =~ '(?i).*phil.* return c, r , connected;

merge (F:Genre {nom:'Féminin'})
merge (M:Genre {nom:'Masculin'})
Match (cand: Candidat)
    with cand, cand.sexe as s, F, M
    with cand, CASE s WHEN 'F' THEN F Else M end AS genre

merge (cand)-[:GENRE]->(genre)
return count(cand) as nb_candidats_avec_genre;

match (cand:Candidat)-[:GENRE]->(g:Genre)
return g.nom as genre, count(cand) as nb_candidats;


/// Création des nœuds TailleVille
MERGE (t1:TailleVille {nom:'1-Très petite'})
MERGE (t2:TailleVille {nom:'2-Petite'})
MERGE (t3:TailleVille {nom:'3-Moyenne'})
MERGE (t4:TailleVille {nom:'4-Grande'})
MERGE (t5:TailleVille {nom:'5-Très grande'})

/// Lier chaque commune à sa taille
MATCH (c:Commune)
    WITH c,
    CASE
        WHEN c.population < 2000 THEN t1
        WHEN c.population < 10000 THEN t2
        WHEN c.population < 20000 THEN t3
        WHEN c.population < 100000 THEN t4
    ELSE t5
    END AS taille

MERGE (c)-[:A_TAILLE]->(taille) ;


match (t:TailleVille) DETACH DELETE t;


match (c1: Commune {codeINSEE: '03190'}), (c2: Commune)
where c1<> c2
    return c2.codeINSEE AS CodeINSEE, c2.name as Commune,
    point.distance(c1.location,c2.location)/1000 as distance_km
order by distance_km asc limit 10;


/*match (c1:Commune)
match (c2:Commune)
    where c1<>c2

with c1,c2, point.distance(c1.location, c2.location) as dist order by dist asc
with c1, collect({node: c2, distance: dist})[0..3] as top3 unwind top3 as t
with c1, t.node as c2.node, t.distance as dist merge (c1)-[r:Proche]->

*/

match (start:Commune {codeINSEE:'92035}), (end:Commune {codeINSEE:'92002})
Match path = shortestPath((start)-[:Proche*]-(end))
return nodes(path) as communes, relationships(path) as liens, [r IN relationships(path) | r.distance/1000] as distance_km;

```
