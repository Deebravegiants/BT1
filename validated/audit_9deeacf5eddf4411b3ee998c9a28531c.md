### Title
Webhook `shop` (and `topic`/`webhook_id`) headers are not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw request body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Registry.process` validates only that the body's HMAC matches, then dispatches the handler using the unauthenticated `shop` header as the tenant identity. Because Shopify signs webhooks with the app's single `client_secret`, which is identical for every shop that installs the app, any actor who legitimately installs the app on their own shop can capture a valid `(body, hmac)` pair from their own genuine webhook traffic and replay it to the app's webhook endpoint while substituting the victim's `shop-domain` header. The signature still validates because the shop identity was never part of the signed content.

### Finding Description
The `hmac` covers only `@raw_body`: [1](#0-0) 

`shop` is read straight from headers with no binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) to build the dispatched metadata: [3](#0-2) 

`HmacValidator.validate` computes the digest solely from `to_signable_string` (the raw body), never incorporating `shop`, `topic`, or `webhook_id`: [4](#0-3) 

The binding that should hold is: `hmac == HMAC(secret, body || shop || topic)`, i.e., the tenant (`shop`) that the handler acts on should be cryptographically bound to the signature that authenticates the request. Instead the equality actually enforced is only `hmac == HMAC(secret, body)`, with `shop` supplied out-of-band and unauthenticated. Since Shopify uses one `client_secret` per app (shared across every merchant/shop that installs it), a valid `(body, hmac)` pair generated for shop A's webhook remains a valid `(body, hmac)` pair when replayed with the `shop-domain`/`x-shopify-shop-domain` header changed to shop B — `HmacValidator.validate` cannot detect the substitution because `shop` never enters the signable string.

### Impact Explanation
This breaks tenant isolation (cross-tenant access), one of the explicitly listed Critical impacts. An attacker who is a legitimate merchant of the target app (a normal, unprivileged capability — installing an app on one's own store requires no special privilege) can observe genuine webhook deliveries sent to their own endpoint (same body/HMAC scheme, same shared secret) and replay that exact request to the shared webhook endpoint with the victim's shop domain in the header. Any host application that uses `request.shop` from `ShopifyAPI::Webhooks::Registry`/`Request` (as the library's own API and documentation instruct developers to do, e.g., to look up which merchant record a webhook body applies to) will process attacker-controlled data as if it originated from the victim shop, allowing data injection/corruption across tenant boundaries without ever touching the victim's credentials.

### Likelihood Explanation
Moderate-to-high: it requires the attacker to run their own instance of the app (a normal, permissionless action for any public app), capture one legitimate webhook of a topic that is replay-value (e.g., an idempotent/side-effect-producing topic), and then simply swap the `shop-domain` (or `x-shopify-shop-domain`) header value on replay to the same, single, shared webhook endpoint. No secret compromise, TLS interception, or privileged account is required — this is exactly the "unprivileged internet user" analog requested: the attacker only needs to be a self-service, low-privilege merchant of the same app.

### Recommendation
Bind the tenant-identifying fields into the authenticated signature/verification, e.g., include `shop` (and ideally `topic`, `webhook_id`) in `Webhooks::Request#to_signable_string`, or otherwise re-verify (out of band, e.g. against session/shop store) that the `shop` header corresponds to a shop that the app actually expects for this specific HMAC before dispatching the handler. At minimum, document prominently that `request.shop` is not authenticated by the HMAC and must not be trusted as a tenant selector without additional verification (e.g., cross-checking against a known list of installed shops plus rate-limiting/idempotency on `webhook_id`).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook to the app's endpoint:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`
   - Body: `{"id": 1, ...}`
3. Attacker replays the identical body and HMAC to the same public endpoint, only changing the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` as `victim.myshopify.com` (`lib/shopify_api/webhooks/request.rb:20-23`).
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it validates the body against the shared app secret only (`lib/shopify_api/utils/hmac_validator.rb:12-31`), independent of the `shop` header.
6. The host application's handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's body>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`) and processes attacker-controlled data under the victim tenant's identity.

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
