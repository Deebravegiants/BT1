### Title
Webhook `shop` identity is trusted for tenant dispatch without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the handler using a `shop` value that comes from an HTTP header which is never included in the signed content. This breaks the identity binding `shop authenticated by the HMAC == shop used to route/attribute the webhook`, analogous to the report's core issue: a field that drives sensitive action logic (here, tenant attribution) is not bound to the data that was actually authenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is completely outside the signed content: [2](#0-1) [3](#0-2) 

`Registry.process` validates the HMAC (which only covers the body) and then immediately trusts `request.shop` to build the `WebhookMetadata` object that is handed to the host app's handler for per-tenant processing: [4](#0-3) 

`Utils::HmacValidator.validate_signature` computes the signature strictly from `verifiable_query.to_signable_string` (i.e. the body only) and compares it to the `hmac` field, again never touching `shop`: [5](#0-4) 

Because the equality the gem is supposed to enforce is `shop that produced/authorized this signed payload == shop passed to the handler`, and the `shop` header is not part of the signed bytes, that equality is never actually checked by the gem — it is left entirely to the host application (if it even notices).

### Impact Explanation
For any two shops that install the same app (a normal, expected multi-tenant condition — no privileged access or leaked credentials required beyond what any installed shop already has), a webhook payload with a valid HMAC for shop A's body can be delivered/replayed with the `shopify-shop-domain` header set to shop B. `Registry.process` will pass this to the handler as `WebhookMetadata.new(shop: "shop-b...", body: <shop-a's body>, ...)`. Any host code that uses `request.shop` (as recommended and shown in this gem's own docs) to select which tenant's data/session to update will attribute shop A's webhook content to shop B — a cross-tenant data integrity issue purely due to the gem failing to bind the authenticated identity to the field used for dispatch.

### Likelihood Explanation
This does not require intercepting TLS, leaking the `client_secret`, or any privileged access — an attacker only needs the ability to relay/replay an HTTP request they observed (e.g., a malicious or compromised intermediary, or any actor capable of capturing one legitimate webhook delivery and re-sending it with a modified header) since the header is never authenticated. This is a design gap directly inside the gem's `Webhooks::Request`/`Registry` code path, not a misuse of a documented API by the host application.

### Recommendation
Include `shop` (and ideally `topic`, `api_version`, `webhook_id`) as part of the HMAC-signed content, or otherwise re-derive/cross-check the tenant identity from a source that is cryptographically bound to the signature before dispatching to handlers, so that `Registry.process` cannot be fed a valid-body/mismatched-shop combination.

### Proof of Concept
1. Shop A's store triggers a webhook; Shopify sends a request with body `B` and header `shopify-shop-domain: shop-a.myshopify.com`, HMAC `H = HMAC(secret, B)`.
2. An attacker who can observe/replay this request (e.g., via a compromised proxy, logging pipeline, or any relay point before the app's endpoint) resends the same body `B` and HMAC `H`, but changes the header to `shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: modified_headers)` builds successfully; `hmac` returns `H`, `shop` returns `"shop-b.myshopify.com"`.
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B) == H` — this passes because `B` and `H` are unchanged.
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: parsed(B), ...)`, causing shop A's webhook content to be processed under shop B's tenant context.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
