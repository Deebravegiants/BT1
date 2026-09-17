# [M] Open WebUI: Deletion of directories and file embeddings in other knowledge bases via sync cleanup

## Summary
Severity: Medium
Advisory: GHSA-jxc9-xmc4-gr23
CVE: CVE-2026-70488
CWE: CWE-639, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-jxc9-xmc4-gr23
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0.9.6 <0.11.0

## Details
## Summary
A user with write access to one knowledge base could delete directories, and drop file embeddings, belonging to knowledge bases they do not control. The sync cleanup endpoint verified write access on the knowledge base named in the URL and then acted on the directory and file ids supplied in the request body without checking that those objects belonged to that knowledge base.

## Preconditions
Default configuration, no flags involved. The attacker needs write access to at least one knowledge base, which comes from owning one, from a write access grant, or from the admin role; `workspace.knowledge` is off by default, so an ordinary user cannot simply create one. They also need the victim's directory or file id, which are UUIDs and are not enumerable, so in practice the attacker is someone who can already see the target knowledge base, typically a read-only collaborator on a shared one. Deployments where no knowledge base is shared beyond its owner are not reachable.

## Impact
The attacker deletes a target directory and, because the deletion runs without moving files to the parent, the knowledge_file associations for every file in that subtree are removed as well, so those documents silently drop out of the victim's knowledge base and out of its retrieval results. Separately, the per-file vector cleanup dropped the standalone `file-<id>` collection for any file id, breaking chat-with-file for that document. The stored files and their database rows survive, since that path was gated on file ownership, and an owner can restore the state by re-adding and reprocessing. Nothing about the target knowledge base's contents is disclosed to the attacker.

## Fix
Fixed in https://github.com/open-webui/open-webui/pull/26722. Both request-body loops are now scoped to the knowledge base in the URL: a directory is resolved and skipped unless its `knowledge_id` matches, and the per-file vector cleanup runs only for files that are members of that knowledge base. Upgrading fully resolves the issue.

## Root cause
Affected component: `backend/open_webui/routers/knowledge.py`, handler `sync_knowledge_cleanup`, endpoint `POST /api/v1/knowledge/{id}/sync/cleanup`. Affected setup: all builds from 0.9.6 onward, no optional dependency involved.

The handler treated the write-access check on the URL knowledge base as authorization for everything it went on to do, but the objects it acted on came from the request body and were addressed by primary key alone. Directory deletion at the model layer deletes by directory id and has no notion of a parent knowledge base, so the only thing that could have bound the two together was a membership check in the handler, and there was none. The explicit directory-delete endpoint in the same router already carried that check, which is what makes this a gap in one handler rather than a missing model-layer control.

## Credits
Reported by @whyiug.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-jxc9-xmc4-gr23
- https://github.com/open-webui/open-webui/pull/26722
- https://github.com/open-webui/open-webui/commit/707efeaed7992dd9896d5928559458f228b9a539
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.11.0
