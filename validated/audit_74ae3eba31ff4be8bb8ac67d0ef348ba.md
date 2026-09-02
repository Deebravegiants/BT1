### Title
Webhook HMAC signature does not bind the `shop-domain` header, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, while the `shop` (tenant) attribution used by the host application's webhook handler is taken from the `X-Shopify-Shop-Domain` header, which is never included in the signed bytes. Any party who can obtain one genuine, validly-signed webhook body/HMAC pair for a shop they control can replay that exact body+HMAC with a forged `shop-domain` header to make the receiving app believe the payload belongs to a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from an unauthenticated HTTP header with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which computes the HMAC over `to_signable_string` (i.e. the body only) and compares it to the `hmac` header, then immediately forwards `request.shop` (the unauthenticated header) to the handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate`/`validate_signature` confirm this: they only ever operate on `verifiable_query.to_signable_string`, never on the `shop` field of the query object: [4](#0-3) 

This breaks the intended identity binding: `HMAC-verified bytes == raw body only`, while `shop attributed to the webhook == header value`, i.e. `verified bytes != acted-upon tenant identity`. This is the same class of bug as the report's `step()` issue: a security-critical assignment/attribution (bond recipient there, tenant/shop here) is derived from an operator-supplied value that is disjoint from what was actually authenticated (the state used in the `step` proof there, the raw body here).

Any user who has installed the app on their own shop receives genuine webhooks with a valid HMAC computed by Shopify using the app's `client_secret` over the JSON body for their own shop. Because the `shop-domain` header is not part of the signed payload, that same attacker can replay the identical body and HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value (e.g., a victim shop's domain). `Utils::HmacValidator.validate` still returns `true` because the body is unchanged, and `Registry.process` will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen value.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (or `Request#shop`) to look up/update tenant-specific data (which is the documented, intended use — see `docs/usage/webhooks.md` and `WebhookMetadata`), an attacker can cause data to be written, deleted, or otherwise processed under a victim shop's identity using content the attacker controls, purely by forging one HTTP header on a replayed, still-validly-signed request. This is a cross-tenant access/data-integrity issue rooted in the gem's own authentication primitive (`HmacValidator`), not a host-application misuse, since the gem exposes `request.shop` as if it were authenticated alongside the body.

### Likelihood Explanation
Requires only that the attacker be a legitimate (even free/trial) installer of the target app, able to trigger a webhook for their own shop and capture its raw body + HMAC header, then POST it to the app's public webhook endpoint with a modified `shop-domain` header — no access token, `client_secret`, or privileged access is needed.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) into the signed material, or otherwise cryptographically tie the header-derived shop to the authenticated payload (e.g., require the caller to also validate that the HMAC was computed by Shopify for the specific shop by cross-checking against a known/registered shop-token pairing) before trusting `Request#shop` for tenant attribution. At minimum, document clearly that `Request#shop` is unauthenticated and must not be used to resolve tenant-scoped resources without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":1}` with header `x-shopify-hmac-sha256: <valid HMAC over the body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` because it only checks `request.to_signable_string` (the raw body), which is unchanged.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) proceeds to call the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: {"id":1}, ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
