from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session :
        result = session.run("MATCH (n) RETURN count(n) AS total")
        print(result)
        print(result.single()["total"])

        result = session.run(
            "MATCH (c:Commune {codeINSEE: $code})-[r]-(connected) RETURN c, r, connected",
            code = "03190"
        )
        for record in result :
            commune = record["c"]
            relation = record["r"]
            connecte = record["connected"]
            print(f"{commune['name']} --[{relation.type}]--> {connecte['name']}")