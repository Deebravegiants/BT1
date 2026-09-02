Found in `lib/shopify_api/webhooks/request.rb`: the `shop` field used to route/authorize a webhook to a merchant tenant (`Request#shop`, read from the `shopify-shop-domain` header) is **not included in the HMAC-signed bytes**. `to_signable_string` returns only `@raw_body`, so the signature binds the request *body* to the secret, but never binds the *shop* claimed by the header. [1](#0-0) [2](#0-1) 

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook delivery to any registered handler - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload as `to_signable_string == @raw_body` only. The `shop` (and `topic`) values are taken from unauthenticated HTTP headers (`shopify-shop-domain` / `x-shopify-shop-domain`) and are never mixed into the signed bytes. `Registry.process` validates the HMAC of the raw body, then unconditionally trusts `request.shop` when constructing `WebhookMetadata` passed to the app's handler.

### Finding Description
`HmacValidator.validate` calls `verifiable_query.to_signable_string` to build the signed string and compares it to the received `hmac`. [3](#0-2)  For `Webhooks::Request`, this signable string is only the raw body: [2](#0-1)  — the `shop` header is read separately via `shopify_header("shop-domain")` and is not part of what is signed [1](#0-0) .

`Registry.process` then does:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [4](#0-3) 

The equality that should hold is: `shop_bound_by_hmac == shop_delivered_to_handler`. Because the HMAC only covers `@raw_body`, this equality never actually holds — the gem verifies "these bytes were HMAC'd with our secret" but trusts an entirely separate, attacker-controlled header for tenant attribution. Any party that has (or can guess/replay) one legitimate raw-body+HMAC pair for their own shop can resend the same body with a forged `x-shopify-shop-domain` header claiming to be a different shop; the signature still validates (it only checks the body), and the app's webhook handler is invoked believing the event came from the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion at the boundary the gem is explicitly responsible for (`Utils::HmacValidator` / `Webhooks::Registry.process` exist specifically to authenticate that a webhook came from Shopify for a specific shop). If the host application's webhook handler uses `data.shop` to decide which merchant's data to read/write/update (the documented and expected usage pattern, as shown in the registry tests and `WebhookMetadata`), an attacker who can produce or replay any valid signed body (e.g., their own shop's webhook, or a body whose HMAC happens to be reusable/publicly observable) can cause the handler to process it under a spoofed victim `shop`, leading to cross-tenant data corruption or disclosure inside the app's own webhook processing. This matches "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to be able to submit HTTP requests to the app's webhook endpoint with attacker-chosen headers and a body+HMAC pair that validates — this is straightforward for an unprivileged internet user for any shop where they can trigger the app to send *them* a legitimately-signed webhook body (e.g., install the app on their own shop, trigger an event, capture the raw body and its valid HMAC), then replay that exact body against the endpoint with the `shop` header changed to a victim shop. Since `shop` is not bound into the signature, the tampered request still passes `HmacValidator.validate`.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the value that must be authenticated, or explicitly document/enforce that `request.shop` must not be trusted for authorization decisions without additional binding. Concretely, Shopify's real webhook HMAC only ever covers the raw body by design, so the fix should be to have `Registry.process` cross-check `request.shop` against an out-of-band trusted source (e.g. only invoke handler for shops with an active offline session in the host app) rather than trusting the header verbatim, or add documentation making unmistakably clear that `shop` is unauthenticated and must be re-validated by the host application against known installed shops before using it to select tenant data.

### Proof of Concept
1. App receives a legitimate webhook for `attacker-shop.myshopify.com` with raw body `B` and valid header `x-shopify-hmac-sha256` computed as `HMAC-SHA256(secret, B)`.
2. Attacker captures `B` and its valid `hmac` value (trivial if attacker owns `attacker-shop`, or if `B` is guessable/constant such as `{}` in test fixtures).
3. Attacker POSTs the same `raw_body: B` with headers `x-shopify-hmac-sha256: <same hmac>`, `x-shopify-shop-domain: victim-shop.myshopify.com`, `x-shopify-topic: <topic>` to the app's webhook endpoint.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` — this still matches, since `B` is unchanged. [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process/act on data under the victim's tenant identity despite the request never having been authenticated for that shop. [6](#0-5)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
