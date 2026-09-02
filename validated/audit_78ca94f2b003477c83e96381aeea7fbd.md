### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-signing only the raw request body, while the `shop-domain`, `topic`, `api-version`, and `webhook-id` headers are read directly from unauthenticated headers and passed on to the app's handler untouched. Because all shops installing the same app share one `api_secret_key`, an attacker who can obtain one validly-signed webhook body/HMAC pair (e.g., by installing the app on their own store and receiving a real webhook) can replay that exact body+HMAC to the app's webhook endpoint while substituting a victim shop's domain in the `shop-domain` header. `HmacValidator.validate` will still pass because the signature never covered the header, and `Registry.process` will hand the forged shop identity to the app's handler as if it came from the victim.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` accessors are read straight from HTTP headers, none of which are part of the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` (i.e. the body only) and compares it to the `hmac` accessor (also header-derived): [3](#0-2) 

`Registry.process` gates only on this HMAC check, then immediately trusts `request.shop`, `request.topic`, etc., to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: **shop authenticated by the HMAC == shop delivered to the handler**. Because the header carrying `shop-domain` is excluded from the signable string, this equality is not enforced — the HMAC only proves "this body was HMAC'd with our shared secret at some point," not "this body was HMAC'd for this shop." Any party who can obtain one legitimately-signed body/HMAC pair for their own tenant (trivial: install the app on any store, or receive any real webhook) can resubmit that pair to the app's public webhook endpoint with an arbitrary `shopify-shop-domain` header (or `x-shopify-shop-domain`), and the check in `Registry.process` will pass, causing the handler to run believing the webhook originated from a different, victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to guarantee to host applications: `WebhookMetadata#shop` is the field apps use to determine which merchant's data to update/act on `(lib/shopify_api/webhooks/webhook_handler.rb:6-12)`. A forged `shop` value flowing through a "verified" webhook request enables cross-tenant confusion in any application that trusts `data.shop` after `HmacValidator.validate` succeeds — data can be attributed to, or actions taken against, the wrong merchant. This matches the Critical impact category "cross-tenant access."

### Likelihood Explanation
Low-to-moderate. It requires the attacker to obtain at least one validly HMAC-signed webhook body for the shared app secret — achievable by any user who installs the (public) app on their own shop and captures a real webhook delivery (body + `hmac-sha256` header), or by triggering a specific topic (e.g. `app/uninstalled`) whose body content doesn't reveal shop-specific details relevant to the exploit. No access token, secret key, or privileged account is required — only the ability to send an HTTP POST to the app's public webhook endpoint with a crafted `shop-domain` header.

### Recommendation
Include the shop domain (and ideally topic / webhook id) in the signed material, or otherwise cryptographically bind the header claims to the body before trusting them — e.g., verify that `shop-domain` corresponds to a shop the app actually installed for that specific webhook subscription, or require the gem to fail closed if the `shop-domain` header cannot be independently corroborated. At minimum, document prominently that `request.shop` is unauthenticated header data and must not be trusted for tenant selection without additional verification (e.g., cross-checking against the app's own installed-shops list) before use.

### Proof of Concept
1. Attacker installs the victim app on their own store `attacker.myshopify.com` and captures one real, validly-signed webhook delivery: raw body `B` and header `shopify-hmac-sha256: H` (where `H = HMAC-SHA256(api_secret_key, B)`).
2. Attacker sends a POST to the app's webhook endpoint with the same body `B` and header `shopify-hmac-sha256: H`, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` builds successfully (all required headers present) `(lib/shopify_api/webhooks/request.rb:45-63)`.
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` and compares to `H` — this matches because `B` and `H` are unchanged and shop is not part of the signed string `(lib/shopify_api/webhooks/registry.rb:188-190, lib/shopify_api/utils/hmac_validator.rb:12-31)`.
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` `(lib/shopify_api/webhooks/registry.rb:198-199)`, causing the host application to process a forged webhook as if it came from the victim shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
