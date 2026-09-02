### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying the HMAC over the raw request body. The `shop` and `topic` values that the app subsequently trusts to identify the tenant and dispatch the handler are read directly from HTTP headers that are never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` and `topic` accessors are parsed straight out of the (unauthenticated) headers, with no HMAC coverage: [2](#0-1) 

`Registry.process` verifies the HMAC (`Utils::HmacValidator.validate(request)`, which internally calls `to_signable_string` — i.e. only the body) and then immediately hands the *unverified* `request.shop` and `request.topic` to the handler: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`, which for a `Webhooks::Request` is just the raw body, and compares it with `OpenSSL.secure_compare`: [4](#0-3) 

This breaks the intended identity binding `HMAC-verified(shop) == shop used for tenant dispatch`. Any legitimate (unprivileged) merchant who has installed the app receives genuinely-signed webhooks at their own endpoint. Because the shop-domain and topic headers are excluded from the signed payload, that merchant can capture a valid `(raw_body, hmac)` pair from their own shop and replay it to the app's shared webhook endpoint with the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header rewritten to name a *different* shop. `HmacValidator.validate` still succeeds (it only checks the body/secret), so `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen shop while the body content actually originated from the attacker's own shop. Contrast this with the OAuth `AuthQuery`, where `shop` is one of the fields explicitly included in `to_signable_string` and is therefore HMAC-bound: [5](#0-4) 

That contrast highlights that the webhook `shop`/`topic` fields are an outlier: they are "acted on" (used to key persistence/dispatch by consuming apps, per this gem's documented `WebhookMetadata#shop` API) but are not bound by the HMAC that the gem itself performs.

### Impact Explanation
Consuming applications are expected to use `WebhookMetadata#shop` to key per-tenant records (this is the very reason `Registry.process` exposes it to the handler). Because that field is unauthenticated, a merchant with a valid app installation can inject a webhook payload under an arbitrary victim shop's identity, since the gem's own HMAC check does not bind `shop` to the signed bytes. Depending on how the handler uses `data.shop` (e.g., to look up which merchant's data record to mutate), this can result in cross-tenant data corruption/write into another merchant's records — a cross-tenant access impact rooted entirely in this gem's authentication primitive (`HmacValidator`/`Webhooks::Request`), independent of any host-application misuse.

### Likelihood Explanation
Requires only an existing, unprivileged installation of the app by the attacker (no access token, no `api_secret_key`, no privileged account) — they only need to capture one of their own legitimate webhook deliveries and replay it with a modified `shop-domain`/`topic` header to the app's public webhook endpoint. This is fully within reach of a normal internet-facing attacker who is simply a customer/merchant of the app.

### Recommendation
Include `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) in the HMAC-signed material, or otherwise cryptographically bind the shop identity to the signature (e.g., verify HMAC using a per-shop secret keyed to the claimed shop, and reject if it doesn't match), so that `HmacValidator.validate` cannot succeed unless the shop header actually corresponds to the source of the signed bytes.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook: body `{"id":1}"`, header `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker resends this exact `(body, hmac)` pair to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header; `Utils::HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) succeeds because it only hashes `@raw_body`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
