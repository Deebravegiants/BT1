### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) are trusted from unauthenticated headers while only the raw body is covered by the HMAC — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking that `Utils::HmacValidator.validate(request)` succeeds, and `Request#to_signable_string` returns only `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` values consumed downstream (and handed to app webhook handlers via `WebhookMetadata`) come straight from HTTP headers that are never included in the signed string, so they are unauthenticated with respect to the HMAC check.

### Finding Description
`HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` is defined to return only the raw request body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from separate, unsigned headers: [3](#0-2) 

`Registry.process` only checks the HMAC before dispatching, and then forwards the unauthenticated `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` into `WebhookMetadata`, which is delivered to the app's handler as trusted, verified data: [4](#0-3) 

The identity binding that should hold is: `bytes verified by HMAC == bytes the app treats as authenticated (including shop attribution)`. Here that equality is broken — the HMAC binds only the body, not the shop/topic/webhook-id headers, yet `Registry.process` and `WebhookMetadata` treat the headers as if they were verified alongside the body.

Because `api_secret_key` is a single per-app secret shared across every merchant that installs the app (not a per-shop secret), any unprivileged internet user can install the target public app on their own shop, receive a legitimately HMAC-signed webhook delivery for their own shop, and then replay that exact raw body (with its valid, unmodified HMAC) to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header to a different (victim) shop's domain. `HmacValidator.validate` still passes, because only the body — which the attacker did not modify — is checked. The handler then executes attacker-controlled body content attributed to the victim shop.

### Impact Explanation
This crosses a tenant boundary: an attacker who controls one tenant (their own shop, or any shop that installed the multi-tenant app) can get a webhook payload attributed to a different tenant, because the field the app uses to select which merchant's data to update is not bound to the same cryptographic check as the payload. This matches "cross-tenant access" (Critical) — the confidentiality/integrity separation between shops that install the same app is broken by design of this gem's `Request`/`Registry` verification, not by any host-application misuse of a documented safe API (the gem provides no mechanism to bind shop/topic to the HMAC).

### Likelihood Explanation
Likelihood is Medium: exploitation requires the attacker to be able to install (or otherwise trigger) the public app on a shop they control in order to obtain one legitimately-signed webhook body/HMAC pair, then replay that raw body against the shared webhook endpoint with a forged shop header. No secret material, TLS interception, or privileged account is required — only the ability to receive a webhook as an ordinary merchant/installer of the app, which is a normal unprivileged capability for public Shopify apps.

### Recommendation
Bind the shop (and ideally topic/webhook-id) to the same authenticated bytes checked by the HMAC — e.g., include the `shop-domain`, `topic`, and `webhook-id` headers in the canonical string signed/verified via `to_signable_string`, or independently verify that the `shop` header matches an `shop_domain`/`shop` field embedded in the parsed body/GraphQL data before trusting it for tenant routing. At minimum, cross-check the header-derived `shop` against a shop identifier that is itself covered by the HMAC.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook (e.g., `orders/create`) — this delivery has a valid `X-Shopify-Hmac-Sha256` computed over the raw JSON body using the app's shared `api_secret_key`.
2. Attacker captures the raw body and its valid HMAC (they legitimately received this delivery to their own endpoint/logging proxy — no MITM needed).
3. Attacker resends the identical raw body and HMAC to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally alters `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `HmacValidator.validate` in [5](#0-4)  succeeds because it only re-hashes the unmodified body.
5. `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-controlled content as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
