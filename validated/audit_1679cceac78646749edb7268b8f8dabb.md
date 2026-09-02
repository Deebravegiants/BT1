## Analysis

Mapping the report's bug class ("a field is acted upon after only *part* of the transaction/state was verified") onto this gem's identity-binding rule set, the strongest analog is in the webhook-processing pipeline: **the `shop`, `topic`, `webhook_id`, and `api_version` fields that the gem uses to attribute an incoming webhook to a tenant are never covered by the HMAC signature that authenticates the request.** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook shop/topic identity is trusted from unauthenticated headers while only the raw body is HMAC-verified, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` verifies solely that the body bytes match a signature computed with `Context.api_secret_key`. The `shop`, `topic`, `webhook_id`, and `api_version` values — all read directly from HTTP headers — are never part of the signed payload. `Registry.process` trusts these header-derived values to build `WebhookMetadata` and dispatch it to the host app's handler, even though they carry no cryptographic binding to the authenticated body.

### Finding Description
The equality that should hold is: `shop-that-signed-the-webhook == shop-attributed-to-the-webhook-by-the-gem`. Instead, the gem only proves `raw_body` was HMAC-signed by `Context.api_secret_key`; it never proves that the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, the `topic` header, or the `webhook_id` header originated from the same signed request context as that body.

- `Request#to_signable_string` → `@raw_body` only: [1](#0-0) 
- `Request#shop`, `#topic`, `#webhook_id`, `#api_version` are all pulled from raw headers with no cryptographic tie to the body: [5](#0-4) 
- `HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` header — again, body-only: [6](#0-5) 
- `Registry.process` gates only on this body-HMAC check, then builds tenant-identifying `WebhookMetadata` straight from the unauthenticated headers and hands it to the host app's handler: [3](#0-2) 

Any party who can obtain one genuinely-signed `(raw_body, hmac)` pair from Shopify for their **own** shop (e.g. by installing the app on a shop they control) can replay that exact body+HMAC to the app's webhook endpoint while substituting arbitrary `shop-domain`, `topic`, `webhook-id`, and `api-version` headers. `Utils::HmacValidator.validate` still succeeds because it only checks the body against the secret; `Registry.process` then invokes the topic's handler with `WebhookMetadata` claiming an attacker-chosen `shop` and `topic`, which the host application will treat as authentic per-tenant Shopify data.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: a request that is only proven authentic for the attacker's own shop is processed as if it were authentic for **any shop and any topic the attacker chooses to declare in headers**. Depending on how the host app's handlers use `WebhookMetadata#shop`/`#topic` (a documented, expected usage pattern for this gem), this can drive actions scoped to a victim tenant — e.g. triggering `app/uninstalled` cleanup, GDPR `customers/data_request`/`shop/redact` handling, or business-logic side effects — using data that never came from the victim shop. This is cross-tenant impact within the gem's own trust boundary (the HMAC check it performs), independent of any host-app misuse.

### Likelihood Explanation
Reachability requires only that an attacker can trigger one genuine webhook for a shop they legitimately control (any developer/merchant who installs an app built on this gem satisfies this) and can reach the app's public webhook endpoint — no `api_secret_key`, access token, or privileged account is needed, satisfying the "unprivileged internet user" bar. The header-spoofing step (changing `shop-domain`/`topic`/`webhook-id`) requires nothing beyond normal HTTP client capability.

### Recommendation
Bind the tenant/topic identity into the signed content rather than trusting headers verified separately from the signature: either (a) require the host application to independently verify that the `shop-domain` header corresponds to a shop that actually has this webhook/topic registered and an active session, or (b) have the gem include `topic`, `shop-domain`, and `webhook-id` in the HMAC-covered signable string (mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop`, `code`, `state`, etc. into its HMAC). At minimum, document that `WebhookMetadata#shop`/`#topic` are unauthenticated relative to the HMAC and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and lets Shopify send a real webhook, e.g. `orders/create`, capturing the raw body `B` and the valid `x-shopify-hmac-sha256` header `H` (computed by Shopify with the app's shared secret over `B`).
2. Attacker POSTs to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid for `B`), but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: app/uninstalled`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` succeeds because it only recomputes HMAC over `B`: [7](#0-6) 
4. `Registry.process` looks up the handler for the spoofed topic and invokes it with `WebhookMetadata` carrying the spoofed `shop`, causing the host app to perform tenant-scoped logic for `victim-shop.myshopify.com` triggered entirely by the attacker's own signed traffic.

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

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
