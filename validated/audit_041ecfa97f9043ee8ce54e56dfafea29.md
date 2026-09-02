## Title
Webhook processing trusts the `shop` (and `topic`/`webhook_id`) header without binding it to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the raw request body via HMAC, but hands the caller-supplied `shop-domain` header straight through to the application's webhook handler as the trusted tenant identifier. Because the shop identity is never part of the signed material, any party who can obtain one valid `(body, hmac)` pair for the shared app secret can replay it against the webhook endpoint with an arbitrary `shop-domain` header and have it processed as if it belonged to a different merchant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes/compares the HMAC exclusively over that signable string: [2](#0-1) 

Yet `Registry.process` reads `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all sourced from unauthenticated HTTP headers — and passes them directly into the `WebhookMetadata` object delivered to the app's handler after only the body-HMAC check succeeds: [3](#0-2) [4](#0-3) 

This breaks the identity binding: `shop-domain header == tenant the payload is attributed to` is never verified as `shop-domain header == shop that produced/authorized this body+HMAC`. By contrast, the OAuth callback path in this same gem *does* bind `shop` into the signed material (`AuthQuery#to_signable_string` includes `shop`), showing the correct pattern that the webhook path fails to follow: [5](#0-4) 

Since every shop installing the same app shares the same `api_secret_key` (`Context.api_secret_key`), a valid `(raw_body, hmac)` pair computed for one tenant's webhook is cryptographically indistinguishable from one belonging to any other tenant using that app — the shop is not cryptographically part of the message.

### Impact Explanation
Any unprivileged holder of one legitimate webhook delivery for the app (e.g., an attacker who installs the target app on their own store to receive an authentic `orders/create` or similar webhook with a valid HMAC) can replay that exact body/HMAC to the app's webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop. `Registry.process` only checks the body HMAC, and will invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain, causing the host application to process attacker-controlled data as if it originated from the victim tenant. Depending on how the host app uses `data.shop` (e.g., to look up records, write order/customer data, or scope tenant state), this enables cross-tenant data corruption/injection — a boundary the app relies on this gem to enforce.

### Likelihood Explanation
Any internet user can obtain a valid `(body, hmac)` pair simply by installing the app on their own development/free store and capturing one webhook delivery — no access to the app's `client_secret`, tokens, or victim credentials is required. Forging the `shop-domain` header on the replayed HTTP request requires no special privilege since it is a plain, unauthenticated request header validated by neither TLS nor HMAC.

### Recommendation
Bind the tenant identity into the authenticated material, e.g., include `shop-domain`, `topic`, and `webhook-id` in the value that is HMAC-verified (or require the caller to independently verify that the shop on the request matches an active, previously-established session/webhook registration for that shop before trusting `WebhookMetadata#shop`). At minimum, document prominently that `request.shop`/`WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant-scoping key without additional verification (e.g., cross-checking the shop against a known/allow-listed set of shops that have this webhook registered).

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a real webhook delivery with headers `x-shopify-hmac-sha256: <validHmac>`, `x-shopify-shop-domain: attacker.myshopify.com`, and body `B`.
2. Attacker resends an HTTP POST to the same app webhook endpoint with the identical body `B` and identical `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` — this still matches, since `B` is unchanged: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, and the host application processes attacker-supplied content attributed to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
