# [C] Arbitrary file read  via the bulk imports UploadsPipeline

## Summary
Severity: Critical (CVSS 9.6)
Program: GitLab
Weakness: Path Traversal
Reporter: vakzz
State: resolved
Disclosed: 2022-03-21T14:46:33.605Z
Source: https://hackerone.com/reports/1439593

## Details
### Summary

The bulk imports api does not remove symlinks when untaring the uploads.tar.gz file, allowing arbitrary files to be read and uploaded when importing a group.

When a group has uploads (such as markdown attachments), an `uploads.tar.gz` file will be downloaded and extracted in the `UploadsPipeline`:
https://gitlab.com/gitlab-org/gitlab/-/blob/v14.6.0-ee/lib/bulk_imports/common/pipelines/uploads_pipeline.rb#L15
```ruby
       def extract(context)
          download_service(tmp_dir, context).execute
          untar_zxf(archive: File.join(tmp_dir, FILENAME), dir: tmp_dir)
          upload_file_paths = Dir.glob(File.join(tmp_dir, '**', '*'))

          BulkImports::Pipeline::ExtractedData.new(data: upload_file_paths)
        end
```

Since `untar_zxf` only changes the permissions, any symlinks that are extracted from the tar will remain and be added to the list of file paths. When `load` is called, the symlinks will be followed and used as the content for the new file:

https://gitlab.com/gitlab-org/gitlab/-/blob/v14.6.0-ee/lib/bulk_imports/common/pipelines/uploads_pipeline.rb#L23
```ruby
        def load(context, file_path)
          avatar_path = AVATAR_PATTERN.match(file_path)

          return save_avatar(file_path) if avatar_path

          dynamic_path = file_uploader.extract_dynamic_path(file_path)

          return unless dynamic_path
          return if File.directory?(file_path)

          named_captures = dynamic_path.named_captures.symbolize_keys

          UploadService.new(context.portable, File.open(file_path, 'r'), file_uploader, **named_captures).execute
        end
``` 

This can be used to read any file that the git user has read access to such as secrets.yml or other sensitive files.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/1439593_
