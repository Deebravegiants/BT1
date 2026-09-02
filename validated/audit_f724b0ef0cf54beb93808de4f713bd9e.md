## Title
Webhook `shop` domain is trusted by the handler but is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC of the raw request body, then hands the handler a `shop` value taken from an HTTP header that is never included in the signed payload. The binding the code implicitly assumes — "the HMAC-verified request == the `shop` passed to the handler" — does not actually hold, because the `shop` field is not part of what the HMAC covers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read from a separate, unsigned header: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, and then forwards `request.shop` straight into the handler's `WebhookMetadata`, treating it as if it were verified along with the body: [3](#0-2) 

`Utils::HmacValidator.validate` computes and compares the signature purely from `verifiable_query.to_signable_string` (the body, for webhooks) and the app's `api_secret_key`: [4](#0-3) 

So the equality the library implicitly relies on is:
`HMAC_valid(body, secret) == true` implies `shop header is authentic and belongs to that body`

but the actual guarantee provided is only:
`HMAC_valid(body, secret) == true` implies `body bytes are unmodified`

The `shop` field is acted upon (passed into `WebhookMetadata.new(shop: request.shop, ...)`, i.e., it becomes the tenant identity the handler code will use to route/attribute the event) without being cryptographically bound to the signed body.

### Impact Explanation
Any party who can observe one legitimately-signed webhook delivery for a shop that uses the same app installation (e.g., a merchant who installed the app can see their own webhook traffic, or it leaks via logs/network) can replay that exact body+HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header for a different shop. `Utils::HmacValidator.validate` will still return `true` because it never inspected the header, and `Registry.process` will invoke the handler with the attacker-chosen `shop` value paired with another tenant's event body. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up which merchant's data to update), this enables cross-tenant data confusion/contamination without needing the app's `api_secret_key`, `client_secret`, or any access token.

### Likelihood Explanation
Exploitation requires only capturing one valid webhook delivery (body + HMAC), which is realistic for a merchant that has installed the same public app and can observe traffic to their own endpoint, then replaying it with a modified shop header — no secret material is required. Likelihood is bounded by the difficulty of obtaining a captured payload, but the code path itself imposes no additional check tying `shop` to the signed bytes.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header value in the signable payload verified by the HMAC, or otherwise cryptographically/structurally bind them (e.g., require the host application to independently confirm `shop` against a known/registered session before trusting `WebhookMetadata#shop`). At minimum, document clearly that `WebhookMetadata#shop` is unauthenticated and must be revalidated by the consuming application before being used for any tenant-scoped action.

### Proof of Concept
1. App has two shops installed: `victim-shop.myshopify.com` and `attacker-shop.myshopify.com`, sharing the same `api_secret_key`.
2. Attacker owns `attacker-shop` and observes a legitimate webhook delivery to the app: raw body `B`, header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the same request to the app's webhook endpoint but changes only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over `B` only and still matches `H`: [5](#0-4) 
5. `Registry.process` proceeds and calls the handler with `shop: "victim-shop.myshopify.com"` even though the body `B` actually pertains to `attacker-shop`: [3](#0-2) 
6. If the host application uses `data.shop` to select which tenant's records to mutate/report on, this results in cross-tenant data corruption/leakage triggered entirely by an unprivileged actor who never needed the `api_secret_key`.

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
