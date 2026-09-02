### Title
Webhook shop, topic, and webhook-id headers are trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw HTTP body, so `Utils::HmacValidator.validate` verifies the HMAC exclusively over `@raw_body`. The `shop`, `topic`, `webhook_id`, and `api_version` values, which are read straight from unauthenticated HTTP headers, are never included in the signed content, yet they are the exact fields the library uses to route the webhook to a handler and to identify which merchant/tenant the payload belongs to.

### Finding Description
`Registry.process` gates handling on `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` value returned by the request object: [2](#0-1) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled directly from HTTP headers with no cryptographic binding to that signature: [3](#0-2) 

The identity binding that should hold is:
```
HMAC_secret(signed_bytes) == received_hmac  AND  signed_bytes ⊇ {shop, topic, webhook_id}
```
but the actual implementation only satisfies:
```
HMAC_secret(raw_body) == received_hmac
```
with `shop`/`topic`/`webhook_id` entirely outside `signed_bytes`. Any request whose `raw_body` matches a signature that is valid for the app's single, shop-agnostic `api_secret_key` (e.g. a genuinely Shopify-signed webhook the attacker received for their own store, since they can install the app on their own shop and trigger webhooks with self-chosen resource content) will pass validation with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header value changed to point at a different merchant. `Registry.process` then dispatches to the handler using the forged `request.shop`/`request.topic`, which is passed straight into `WebhookMetadata`: [4](#0-3) 

Because `api_secret_key` is the same for every shop that installs the app (it is not derived per-tenant), a signature that is valid for shop A's payload is equally valid for a replayed request claiming to be shop B, since the shop identifier plays no role in the signature computation.

### Impact Explanation
This is a cross-tenant boundary break: the host application's webhook handlers, written against this gem's documented contract that `Registry.process` "will verify the request did indeed come from Shopify," will process attacker-supplied header values (`shop`, `topic`, `webhook_id`) as trusted, tenant-identifying data despite them never being authenticated. A malicious app-installer can forge webhooks that the host application will attribute to an arbitrary other merchant, causing writes, side effects, or business logic to execute against the wrong tenant's data — a cross-tenant access impact.

### Likelihood Explanation
Any unprivileged internet user who can install the app on their own store (a normal, unprivileged interaction) can obtain a validly HMAC-signed webhook body of their choosing (to the extent Shopify lets them control resource fields), then replay it to the app's public webhook endpoint with the `x-shopify-shop-domain`/`x-shopify-topic`/`x-shopify-webhook-id` headers swapped to target a victim shop. No secrets, tokens, or privileged access are required.

### Recommendation
Include the identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed content that `to_signable_string` returns (or otherwise cryptographically bind them to the HMAC/verification step), so that `Utils::HmacValidator.validate` fails whenever any of these values are altered relative to what Shopify actually signed.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and subscribes to a webhook topic (e.g. `products/update`), shaping the resource so the body contains attacker-chosen values.
2. Shopify sends a legitimately signed webhook to the app's endpoint:
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body under api_secret_key>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-topic: products/update`
3. Attacker replays the identical raw body and `x-shopify-hmac-sha256` value to the same endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present), and `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `raw_body` against the shared `api_secret_key` — the shop header is never part of the signed bytes.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the registered handler with `shop: "victim.myshopify.com"`, causing the host app to act on victim data using an attacker-controlled payload.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```
