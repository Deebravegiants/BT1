### Title
Webhook shop-tenant confusion — the HMAC only covers the request body, not the `x-shopify-shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification performed by `HmacValidator.validate` proves nothing about which shop sent the webhook. `Registry.process` nonetheless trusts the unauthenticated `shop-domain` header to build `WebhookMetadata` handed to the app's handler, breaking the binding `hmac-authenticated body == shop identity used by the handler`.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) [2](#0-1) 

`hmac` is read from the `x-shopify-hmac-sha256` header, and `to_signable_string` returns only `@raw_body`. The `shop` accessor, however, is taken straight from the `x-shopify-shop-domain` header, a value that is never included in the signed payload: [3](#0-2) 

`HmacValidator.validate` computes the HMAC only over `to_signable_string` (the body) and compares it with the received `hmac`: [4](#0-3) 

`Registry.process` accepts the request purely on that body-only HMAC check and then forwards the caller-supplied `request.shop` to the app's webhook handler, unauthenticated: [5](#0-4) 

This is the same class of bug as the external report: an intermediate value (`_r`) was supposed to be included in a calculation but the wrong variable (`s`) was used instead, silently dropping a required binding. Here, the shop identity is supposed to be cryptographically bound to the payload (as it is for real Shopify webhook deliveries, where the whole request is only ever sent for the shop whose body it is), but the gem's verification logic only checks `body == HMAC(body, secret)` and never checks that `shop-domain == shop that produced the body`. Any entity capable of obtaining one valid `(raw_body, hmac)` pair for the app's `client_secret` — e.g., any merchant who has installed the app and thus legitimately receives signed webhooks for their own shop — can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary value in `x-shopify-shop-domain`. The HMAC check still passes (it only re-hashes the body), yet `WebhookMetadata#shop` used by the handler now names a different, victim tenant.

### Impact Explanation
This is a cross-tenant confusion primitive: the handler is invoked believing the (valid, signed) payload belongs to shop B while it was actually produced for shop A. Any host application that uses `data.shop` from `WebhookMetadata` to select which merchant's session/access token/store the webhook content applies to (the intended and documented use of this field) can be made to apply attacker-controlled webhook content to a different tenant's record, or to look up and act using a victim shop's stored access token in response to attacker-supplied data. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
High. No secret material is required beyond a normal, legitimate app installation: any merchant that can trigger a webhook for their own store already possesses a valid `(raw_body, hmac)` pair (their own webhook deliveries are logged/observable to them), and swapping the `shop-domain` header on a replayed HTTP POST to the app's public webhook endpoint requires only a HTTP client.

### Recommendation
Bind the shop identity into the HMAC verification path, e.g. by making `to_signable_string` (or the `hmac` verification call site) include the `shop-domain` header alongside the raw body, or by cross-checking `request.shop` against a value that is otherwise authenticated (such as the recipient endpoint being shop-specific, or verifying shop against Shopify's registered webhook `webhook-id`/subscription metadata rather than trusting the header verbatim).

### Proof of Concept
1. App merchant `attacker.myshopify.com` has the app installed and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H = HMAC-SHA256(client_secret, B)`, `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures `(B, H)` from their own delivered webhook (e.g., via their own endpoint logs).
3. Attacker POSTs to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` returns `true` because it only recomputes `HMAC(client_secret, B)`, ignoring the shop header: [6](#0-5) 
5. `Registry.process` invokes the app handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` even though body `B` was never produced by/for `victim.myshopify.com`.

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
