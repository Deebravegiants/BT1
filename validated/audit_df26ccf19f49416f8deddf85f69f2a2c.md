## Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `Registry.process` validates covers only the raw request body, never the shop header. This breaks the identity binding `HMAC-covered-bytes == bytes-used-for-tenant-attribution`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is pulled from a header that is not part of that signed string: [2](#0-1) 

`Registry.process` validates the HMAC and then dispatches the handler using `request.shop` as the tenant identifier, without any additional binding between the verified bytes and the shop claim: [3](#0-2) 

`HmacValidator.validate` only proves that `secret` produced `hmac` for `to_signable_string` (i.e., the body) — it says nothing about which shop the header claims to be from: [4](#0-3) 

Because the `api_secret_key` is shared across every shop that has installed the app (it is not a per-shop secret), any merchant who has genuinely installed the app can capture one authentic webhook delivery for their own shop (valid body + valid HMAC), and replay that exact body/HMAC pair to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) with a victim shop's domain. `Registry.process` will pass HMAC validation (since the body/HMAC pair is untouched) and will invoke the registered handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain: [5](#0-4) 

This is the same bug class as the H-13 report: a field that is *acted upon* (here, tenant attribution via `shop`) is not *covered by the authentication mechanism* (the HMAC), so the two are silently decoupled and can be driven independently by an attacker.

### Impact Explanation
Any handler that trusts `WebhookMetadata#shop` to decide which tenant's data to create, update, or delete is exposed to cross-tenant data corruption/injection: an unprivileged attacker who is merely a legitimate merchant of the app can inject data attributed to, or trigger actions against, a different, unrelated shop's records — without ever needing the app's `client_secret`, an access token, or any other credential belonging to the victim. This matches the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Exploitation only requires: (1) being an ordinary installed merchant capable of triggering a real webhook (trivial — e.g., updating one's own order/product), (2) capturing that request server-side or via a proxy, and (3) resending it with a modified shop header. No cryptographic secret needs to be known or brute-forced, and no privileged access is required — the shared secret's HMAC continues to validate because the header is never part of the signed content.

### Recommendation
Bind the shop identity into the value that is cryptographically verified, e.g., include the shop domain header in the HMAC-signable string (matching Shopify's actual signing scheme if it does so), or require host applications to independently corroborate `WebhookMetadata#shop` against a shop known to have a valid, stored webhook subscription/session before trusting it for tenant-scoped operations, and document this trust boundary clearly in `docs/usage/webhooks.md`.

### Proof of Concept
1. App merchant A (attacker) installs the app on `shop-a.myshopify.com` and triggers a real webhook (e.g., `orders/create`) so Shopify sends a genuine request with header `X-Shopify-Shop-Domain: shop-a.myshopify.com`, a real body, and a real `X-Shopify-Hmac-Sha256` computed by Shopify using the app's `client_secret`.
2. Attacker intercepts/replays this exact request to the app's webhook endpoint, changing only the header to `X-Shopify-Shop-Domain: shop-b.myshopify.com` (victim shop).
3. `ShopifyAPI::Webhooks::Request.new` parses this successfully (all required headers present), and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over the *unchanged* raw body and secret and succeeds, per: [6](#0-5) 
4. The registered handler executes with `WebhookMetadata.shop == "shop-b.myshopify.com"`, even though the payload actually originated from shop A.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
