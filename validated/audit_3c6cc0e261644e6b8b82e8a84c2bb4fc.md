## Title
Webhook shop-domain (and topic) header spoofing bypasses HMAC identity binding, enabling cross-tenant webhook processing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then dispatches the parsed body to a handler using a `shop` value (and `topic`/`api_version`/`webhook_id`) that are read from unauthenticated HTTP headers. The HMAC never covers these header values, so the "shop identity" that the handler trusts is not bound to the "bytes verified" by the signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers, outside the signed content: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, then immediately trusts `request.shop` (and `request.topic`) to route and label the payload for the handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes/compares the signature purely over `verifiable_query.to_signable_string`, i.e., the raw body, never the headers: [4](#0-3) 

Because the identity fields (`shop`, `topic`) are never part of the signed material, `hmac_valid(body) == true` does **not** imply `shop_header == shop_that_produced_this_body`. Any actor who has legitimately received one authentic (body, HMAC) pair for their **own** shop's webhook — trivially obtainable by installing the app on their own store and receiving any real webhook — can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop domain (and/or the `x-shopify-topic` header for a different registered topic). The HMAC check still passes because the signed bytes (the body) are unchanged; only the unsigned identity headers are forged.

This breaks the intended binding:
`shop header (acted upon by handler)` == `shop bound inside the HMAC-covered bytes` — the equality does not hold, since the right-hand side doesn't exist.

### Impact Explanation
This is a cross-tenant issue: an app's webhook handler (built on top of `WebhookMetadata#shop`) will process/store data under an attacker-chosen shop identity while the actual payload originated from the attacker's own shop. Depending on how the host app uses `data.shop` (e.g., to look up/update per-merchant records), this can lead to writing or triggering business logic against another tenant's data using attacker-controlled webhook content — a cross-tenant access vulnerability reachable by any unprivileged internet user who can install the target app on a shop they control and can send arbitrary HTTP requests to the app's public webhook endpoint.

### Likelihood Explanation
Likelihood is high for apps that expose a public webhook endpoint (a documented, expected use of this gem) and trust `WebhookMetadata#shop` for tenant scoping without independent verification. The attacker only needs: (1) to install the target app on their own shop to obtain one authentic (body, HMAC) pair from Shopify, and (2) the ability to POST directly to the app's webhook URL with modified headers — no access token, `client_secret`, or privileged account is required.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the HMAC-signed material verified against the raw body, or otherwise cryptographically bind them (e.g., derive/validate them from a value covered by the signature) before they are handed to `WebhookMetadata`/handlers. At minimum, document and/or enforce that consumers must independently verify `shop` against their own list of installed/authorized shops before trusting webhook payload routing.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`, obtaining valid webhook deliveries (e.g., `orders/create`) with a genuine `x-shopify-hmac-sha256` computed over the JSON body using the app's shared `api_secret_key`.
2. Attacker captures one such `(raw_body, hmac)` pair.
3. Attacker sends a POST directly to the app's public webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
4. `Utils::HmacValidator.validate` succeeds because it only checks the (unchanged) body against the (unchanged) HMAC — see [5](#0-4) .
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's own body>, ...)` and invokes the registered handler, which now believes this is legitimate data for `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
