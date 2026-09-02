### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) headers are trusted without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body, then unconditionally trusts the `shop-domain` (and `topic`, `api-version`, `webhook-id`) HTTP headers when building the `WebhookMetadata` passed to the app's handler. The identity field that host applications use to route/attribute webhook data to a tenant (`shop`) is never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) [2](#0-1) 

`to_signable_string` returns only `@raw_body`. `shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is completely disjoint from the bytes that are HMAC-verified.

`Registry.process` performs the authentication check and then immediately trusts `request.shop`: [3](#0-2) 

`Utils::HmacValidator.validate` (used here) computes `HMAC-SHA256(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` header: [4](#0-3) 

Because `to_signable_string` is body-only, the equality the code actually proves is:
`HMAC(secret, body_bytes) == received_hmac`

but the equality the host application needs to rely on for tenant attribution is:
`shop_header == shop_that_the_signature_was_computed_for`

These are not the same binding. The `shop` field that flows into `WebhookMetadata.new(... shop: request.shop ...)` and is handed to the app's webhook handler is attacker-controllable header data that is never covered by the cryptographic check, even though `Registry.process` gives the impression that the whole request (including its identifying headers) has been authenticated.

### Impact Explanation
Any party capable of triggering delivery of a legitimately-signed webhook with a particular raw body (e.g., a webhook for their own installed shop, or any webhook whose body content is fixed/predictable — such as empty-body webhooks or webhooks with identical JSON payloads across shops) can replay/re-deliver that request with the `shop-domain` header rewritten to a different shop. `HmacValidator.validate` will still succeed because it only checks the body bytes against the secret, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the forged shop. If the host application uses `WebhookMetadata#shop` to look up which tenant/session the webhook data belongs to (the documented and expected usage pattern), this results in cross-tenant data being attributed to the wrong shop — data/records intended for shop A get processed as if they belong to shop B. This matches the "Critical - cross-tenant access" impact category, since the shop identity binding that gates per-tenant data handling is broken by the library's own authentication routine.

### Likelihood Explanation
Exploitability depends on the attacker controlling or observing at least one validly-signed webhook body for some shop (trivial for their own installed app instance) and being able to redeliver it with a different `shop-domain` header to the app's webhook endpoint — both are realistic for a merchant/attacker who can install the app and capture their own legitimate webhook traffic, then replay it against the same endpoint with a modified header. No possession of the app's `client_secret` or an access token is required.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the HMAC-verified material, or otherwise cryptographically bind the shop-domain header to the signed payload before trusting it in `WebhookMetadata`. At minimum, document/require that consuming applications must not rely on `WebhookMetadata#shop` from `Webhooks::Request` for authorization decisions, and provide an alternate signed carrier (e.g., verify `shop` is echoed inside the signed JSON body where Shopify includes it) rather than the unauthenticated header.

### Proof of Concept
1. App receives a legitimate webhook for `shop-a.myshopify.com` with raw body `"{}"` and a valid `shopify-hmac-sha256` computed over `"{}"`.
2. Attacker (who controls delivery to the app's public webhook endpoint, e.g. by replaying captured traffic) resends the same raw body `"{}"` and the same valid HMAC header, but sets `shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, "{}")`.
4. `ShopifyAPI::Webhooks::Registry.process` builds `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: {}, ...)` and invokes the app's handler as if this were a genuine event for `shop-b`, even though it was never signed for `shop-b`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
