### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from unauthenticated HTTP headers, while `to_signable_string` (the data actually covered by the HMAC) is only the raw request body. This breaks the binding "shop authenticated == shop the HMAC actually covers," allowing an attacker who legitimately receives one genuinely-signed webhook for their own shop to replay it with a forged `shop-domain` header pointing at a victim tenant, and have `ShopifyAPI::Webhooks::Registry.process` accept it as valid and hand it to the handler as if it came from the victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers that are not part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC strictly against `to_signable_string`, i.e. the raw body bytes only, via `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` accepts any `request` whose HMAC validates, then immediately forwards `request.shop` (the unauthenticated header value) into `WebhookMetadata` for the handler to act on: [4](#0-3) 

Because the `shop-domain` header sits entirely outside the HMAC-covered bytes, an attacker who operates their own (unprivileged) Shopify store with the app installed will receive genuinely-signed webhooks from Shopify for their own tenant. The attacker can capture such a webhook (raw body + `X-Shopify-Hmac-Sha256` header) and re-POST it to the app's webhook endpoint after only changing the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header to a victim shop's domain. `HmacValidator.validate` will still succeed because it only checks the untouched body against the untouched HMAC, and `Registry.process` will call the handler with `data.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This is a cross-tenant identity-binding failure: the "shop" that gets authenticated by the HMAC check is not the same "shop" that ends up being trusted by the handler. Any host application logic that keys per-tenant state (billing, GDPR redaction requests, inventory sync, session invalidation, etc.) off `WebhookMetadata#shop` can be tricked into applying attacker-controlled webhook bodies to another merchant's tenant, since the mandatory GDPR topics (`shop/redact`, `customers/redact`, `customers/data_request`) and any custom `:http` registration all funnel through this same unauthenticated `shop` field. This matches the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only that the attacker be an ordinary, unprivileged installer of the app on their own store — a normal, unauthenticated-relative-to-other-tenants capability. No access to the app's `client_secret`, no privileged account, and no interception of TLS to a third party is required; the attacker only replays their own legitimately-received webhook with one header changed.

### Recommendation
Bind the header-derived shop, topic, and webhook id into the signed content the HMAC covers (e.g. verify a canonicalized concatenation of `shop-domain`, `topic`, `webhook-id`, and the raw body, or require the host application to independently confirm that `request.shop` matches the destination tenant/session before trusting it), consistent with the same principle raised in the referenced report about not letting unsigned fields participate in trust decisions.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (no special privilege needed) and triggers/receives a mandatory or custom webhook, capturing the raw body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker resends an HTTP request to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a request whose `to_signable_string` is still `B` and whose `hmac` is still `H`.
4. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(client_secret, B)` and finds it equal to `H`, so validation passes.
5. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: attacker-controlled body ...)`, causing the host app to process attacker data under the victim tenant's identity.

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
