## Title
Biometric Image Data Is Permanently Deleted From Local Storage Even When Upload to Backend Fails - (File: `src/agents/image_uploader.rs`)

## Summary
This is a direct analog to the `TOKE-6` bug class: in the smart-contract report, `destinationIn` is removed from the debt-reporting queue based on the incorrect assumption that "no balance left ⇒ nothing left to settle", even though an unclaimed reward is still pending, causing it to be permanently lost. In `orb-core`'s image upload agent, the local per-signup image directories are unconditionally deleted based on the assumption that "the upload loop finished ⇒ everything was uploaded", even though individual uploads may have failed, causing the biometric data to be permanently lost with no retry path.

## Finding Description
`upload_image()` wraps the actual network request and, on failure, only logs the error and increments a metric — it never returns an `Err`: [1](#0-0) 

That result is awaited by `upload_saved_images()`, and immediately afterward — outside the per-file loop — the whole `image_dir` is removed unconditionally, regardless of whether any of the uploads in the loop actually succeeded: [2](#0-1) 

The same "settle-before-remove" ordering violation repeats one level up in `upload_signup_images()`, which calls `upload_saved_images` for `ir_camera`, `rgb_camera`, `ir_face`, `thermal`, and identification images, then unconditionally removes the entire `signup_dir`: [3](#0-2) 

Additionally, if reading a saved image from disk fails, the code just `continue`s past that image without uploading it, and it is still deleted by the subsequent `remove_dir_all`: [4](#0-3) 

This mirrors the reported root cause exactly: state cleanup (`popAddress`/`remove_dir_all`) is performed based on a "nothing pending" assumption, without first confirming the pending value (reward / biometric image) was actually secured (claimed / durably uploaded).

## Impact Explanation
Biometric image batches (`ir_camera`, `rgb_camera`, `ir_face`, `thermal`, and `identification` images) collected during a signup, which are retained on the Orb specifically so they can later be uploaded to the backend for fraud investigation, debugging, and data-acquisition purposes, are permanently and silently deleted whenever any of the upload requests transiently fail (network error, backend error, or a local disk read error). Because the local copies are removed unconditionally after the upload attempt loop and there is no persistence/retry queue analogous to the `data_uploader`'s persistent `Queue::commit`-on-success pattern, once the directory is removed, the data cannot be recovered or re-uploaded. This falls squarely in the "biometric upload and retention" category — data that should be retained/uploaded is irrecoverably lost due to a cleanup-before-confirmation ordering bug.

## Likelihood Explanation
The code path is triggered during ordinary idle-time uploads (`upload_all_signup_images`), which the comments state are specifically designed to run when the Orb has flaky or delayed Wi-Fi connectivity ("Generally, Orbs in the field will only be in the idle state beyond image_upload_delay if they are connected to Wifi to upload overnight"). Transient network/backend failures under these conditions are a realistic, recurring occurrence rather than a contrived edge case, and every such transient failure causes real, permanent data loss for that signup's images.

## Recommendation
Do not remove `image_dir`/`signup_dir` based on the loop simply completing. Track the actual per-file success/failure of each `upload_image` call (propagate `Err` from `upload_image` instead of swallowing it), and only delete a file/directory once its upload has been confirmed successful. Files that fail to upload should remain on disk to be retried on a subsequent pass, analogous to how `data_uploader`'s persistent queue only calls `commit()`/removes on-disk state after a successful upload confirmation.

## Proof of Concept
1. An Orb performs a signup, producing biometric images under `DATA_ACQUISITION_BASE_DIR/<signup_id>/{ir_camera,rgb_camera,ir_face,thermal,identification}`.
2. Later, `upload_all_signup_images` is invoked during idle state and calls `upload_signup_images(&path)` for that signup.
3. `upload_saved_images` iterates the PNG files; assume the backend returns a transient 5xx error (or the request times out) for one or more files.
4. `upload_image` logs the error and metric but returns `Ok(())` regardless (`src/agents/image_uploader.rs:161-170`).
5. After the loop, `upload_saved_images` unconditionally calls `fs::remove_dir_all(image_dir)` (`src/agents/image_uploader.rs:143`), deleting the images that failed to upload along with any that succeeded.
6. `upload_signup_images` then also unconditionally removes the parent `signup_dir` (`src/agents/image_uploader.rs:190`).
7. The failed images are now gone from both the Orb's local storage and the backend, with no retry mechanism — a permanent loss of biometric data.

### Citations

**File:** src/agents/image_uploader.rs (L127-145)
```rust
    for path in paths {
        let image_id = ImageId::from_image_path(&path)?;
        let img_data = ssd::perform_async(async { fs::read(&path).await }).await;
        let Some(img_data) = img_data else {
            continue;
        };
        upload_image(
            signup_id,
            &image_id,
            presigned_url_type,
            img_data,
            &path.display().to_string(),
            image_dir_name,
        )
        .await?;
    }
    ssd::perform_async(async { fs::remove_dir_all(image_dir).await }).await;
    Ok(())
}
```

**File:** src/agents/image_uploader.rs (L157-171)
```rust
    let response =
        upload_image::request(signup_id, image_id, presigned_url_type, img_data, dd_image_tag)
            .await;
    dd_timing!("main.time.data_acquisition.upload" + format!("{}.full", dd_image_tag), t);
    match response {
        Ok(()) => {
            dd_incr!("main.count.data_acquisition.upload.success" + format!("{}", dd_image_tag));
        }
        Err(e) => {
            dd_incr!("main.count.data_acquisition.upload.error" + format!("{}", dd_image_tag));
            tracing::error!("Uploading image {log_image_path} failed: {e}");
        }
    }
    Ok(())
}
```

**File:** src/agents/image_uploader.rs (L173-192)
```rust
async fn upload_signup_images(signup_dir: &Path) -> Result<()> {
    // extract last element of signup directory path as String
    let signup_id = SignupId::from_signup_dir(signup_dir)?;
    let t0 = Instant::now();
    upload_saved_images(signup_dir, "ir_camera", &signup_id, UrlType::Ir).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.ir_camera", t0);
    let t1 = Instant::now();
    upload_saved_images(signup_dir, "rgb_camera", &signup_id, UrlType::Rgb).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.rgb_camera", t1);
    let t2 = Instant::now();
    upload_saved_images(signup_dir, "ir_face", &signup_id, UrlType::IrFace).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.ir_face", t2);
    let t3 = Instant::now();
    upload_saved_images(signup_dir, "thermal", &signup_id, UrlType::Thermal).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.thermal", t3);
    upload_identification_images_impl(signup_id).await?;
    dd_timing!("main.time.data_acquisition.upload.batch.full_signup", t0);
    ssd::perform_async(async { fs::remove_dir_all(signup_dir).await }).await;
    Ok(())
}
```
