### Title
Webhook `shop`/`topic`/`webhook_id` fields are not covered by the HMAC signature, allowing tenant/topic spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `WebhookMetadata` object built from `shop`, `topic`, `webhook_id`, and `api_version` — none of which are covered by that signature. This breaks the intended identity binding `HMAC(raw_body) == valid ⟺ (shop, topic) is authentic`, since the signature only certifies the body bytes, not the header-derived identity fields the handler relies on to attribute the payload to a tenant/topic.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are pulled straight from HTTP headers, with no cryptographic linkage to the signed content: [2](#0-1) [3](#0-2) 

`Registry.process` validates only the HMAC (computed over the raw body) and then constructs `WebhookMetadata` directly from those unauthenticated header fields, dispatching it to the app's handler as if `shop` were trustworthy: [4](#0-3) 

`HmacValidator.validate`/`validate_signature` confirm only that `verifiable_query.to_signable_string` (i.e., the body) matches the signature computed with `Context.api_secret_key` — it says nothing about which shop or topic that body belongs to: [5](#0-4) 

Because the signature binds only the JSON body, and the `shop-domain`/`topic`/`webhook-id` headers are trusted independently, the equality the code implicitly assumes — `hmac_valid ⟺ (body, shop, topic) authentic` — does not hold. In reality only `hmac_valid ⟺ body authentic` holds; `shop`/`topic`/`webhook_id` are unauthenticated metadata that ride along on the same HTTP request.

### Impact Explanation
An actor who legitimately receives webhooks for one shop (e.g., their own development/test store using the same app and thus the same `api_secret_key`-signed payloads) can capture a valid `(raw_body, hmac)` pair and resend it to the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Webhook-Id`/`X-Shopify-Topic`) header claiming to belong to a different merchant. The HMAC check still passes because it only verifies the body bytes, so the app's handler will process/store data under the attacker-chosen `shop` value. This is a cross-tenant identity-binding break: data intended for shop A can be attributed to shop B inside the host application if it keys any state off `WebhookMetadata#shop`/`#topic`/`#webhook_id` without independent verification — satisfying the "cross-tenant access" high-impact criterion.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one valid `(raw_body, hmac)` pair for the target app (trivially available to any developer/merchant who has installed the app and receives real webhooks), and the ability to POST arbitrary headers to the app's public webhook endpoint (which webhook endpoints are, by design, unauthenticated aside from the HMAC header). No access to `api_secret_key`, access tokens, or privileged accounts is required — only replay of a previously observed legitimate webhook with edited headers.

### Recommendation
Bind the identity fields into the signed material, or otherwise cryptographically tie `shop`/`topic`/`webhook_id` to the signature check:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` (this requires coordinating format with the Shopify webhook signing scheme), or
- At minimum, document/require host applications to independently verify that the `shop` header value matches a shop known to have an active/expected subscription for that `topic`/`webhook_id` before trusting `WebhookMetadata#shop`, and reject requests whose `shop` was not the one used for HMAC computation if Shopify's signing scheme is extended to include it.
- Add a check in `Registry.process` that at minimum cross-references `webhook_id` against previously seen IDs to reject the most trivial byte-for-byte replay case.

### Proof of Concept
1. Install/operate the app on Shop A (attacker-controlled) and Shop B is the victim tenant using the same app installation/`api_secret_key`.
2. Capture a legitimate webhook delivery for Shop A: raw body `B`, and header `X-Shopify-Hmac-Sha256: H` (valid for body `B` under the app's `api_secret_key`).
3. Send a new HTTP request to the app's webhook endpoint with the same body `B` and same `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: shop-b.myshopify.com` (or any target shop) and desired `X-Shopify-Topic`/`X-Shopify-Webhook-Id`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because only the raw body `B` is checked against `H`: [4](#0-3) 
5. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"`, indistinguishable from a genuine webhook for Shop B, even though the payload actually originated from Shop A's data.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
