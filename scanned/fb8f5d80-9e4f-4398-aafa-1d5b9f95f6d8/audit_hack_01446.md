# [H] Pinecone Finance incident: Pinecone launched the pledge pool of protocol token PCT at 09:00 UTC on August 18, 2021, and was attacked at 11:41:19 AM UTC. When

## Summary
Severity: High
Target: Pinecone Finance
Loss: 3,530,000 PCT
Attack method: Compatibility Issue
Published: 2021-08-19
Source: https://medium.com/@PineconeFinance/pinecone-pct%E8%B4%A8%E6%8A%BC%E6%B1%A0%E6%94%BB%E5%87%BB%E4%BA%8B%E4%BB%B6-dfa2b03c8bfc
Type: slowmist-incident

## Details
Pinecone launched the pledge pool of protocol token PCT at 09:00 UTC on August 18, 2021, and was attacked at 11:41:19 AM UTC. When the Pinecone PCT pledge pool went online, the front-end was processed to limit illegal operations, but the hacker bypassed the front-end page during the attack and directly called the smart contract through the ordinary account, depositing PCT tokens greater than the amount of the account balance, and the PCT pool was wrong. Records the number of user deposits. When withdrawing, you can extract more PCT tokens. After discovering that the currency price had plunged, the project party immediately terminated the call of the smart contract. The current loss of the number of PCTs: about 3.53 million.
