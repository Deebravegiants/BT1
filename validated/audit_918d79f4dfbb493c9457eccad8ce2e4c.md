### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant replay of a captured webhook body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body (`to_signable_string` returns `@raw_body`), while the `shop` (and `topic`, `webhook_id`, `api_version`) values used by `Registry.process` to dispatch and attribute the webhook are taken from unauthenticated HTTP headers that are excluded from the signed payload. This mirrors the RocketPool class of bug: a field that is *acted on* (`shop`) is not covered by the value that is *cryptographically verified* (the HMAC).

### Finding Description
`HmacValidator.validate` verifies `request.hmac` against `compute_signature(request.to_signable_string, secret)`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body, and the `shop` accessor reads the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which plays no part in that signed string: [2](#0-1) 

`Registry.process` validates only the HMAC-over-body, then immediately dispatches the handler using the unauthenticated `request.shop` value to attribute the payload to a tenant: [3](#0-2) 

The binding the gem should enforce is: `HMAC_valid(body, secret) == true` implies `shop == the merchant that produced this body`. Because `shop` is excluded from the signed bytes, that equality does not hold — `HMAC_valid` only proves "this body byte-sequence was produced with knowledge of `client_secret`" (i.e., it originated as *some* legitimate Shopify webhook), it proves nothing about which shop header value the request is currently carrying.

### Impact Explanation
An unprivileged internet user who can observe or intercept one legitimate webhook delivery to the app's public webhook endpoint (body + valid `hmac-sha256` header) can replay that exact body/hmac pair while substituting a different `shop-domain` header value (e.g., a victim shop the attacker also has as an installed/test store, or any shop string). `HmacValidator.validate` will still return `true` because the signature check never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` object claiming the data belongs to the attacker-chosen `shop`: [4](#0-3) 

Depending on how the host app's handler uses `data.shop` to key data (a very common pattern documented for this gem, e.g. storing/deleting records per shop), this allows cross-tenant data confusion/injection — writing or deleting records attributed to a shop that never actually sent that payload. This reaches the "cross-tenant access" Critical-impact category defined in scope.

### Likelihood Explanation
Exploitation requires the attacker to have first obtained one valid `(body, hmac)` pair — realistically from their own store's webhook traffic (attackers can install the app on their own development/trial store to legitimately receive signed webhooks) — and then to replay it against the app's public webhook endpoint with a forged `shop-domain` header. No secret, access token, or privileged credential is needed to perform the replay itself; only a previously-observed legitimate payload is required. This is a moderate-likelihood issue: it doesn't require compromising Shopify or the merchant, only using the attacker's own legitimately-received webhook as replay material against other shops' registered handler behavior.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed payload used for HMAC verification, or otherwise cryptographically bind the shop attribution to the verified body (e.g., re-deriving/confirming the shop from data embedded in the verified JSON body rather than trusting the header) before dispatching to a handler in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) so Shopify delivers a legitimately HMAC-signed request: `raw_body = B`, header `x-shopify-hmac-sha256 = HMAC(secret, B)`.
2. Attacker resends the exact same `B` and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only re-hashes `B`.
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...))`, causing the app to process the attacker's own webhook payload as if it belonged to `victim-shop`.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
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
