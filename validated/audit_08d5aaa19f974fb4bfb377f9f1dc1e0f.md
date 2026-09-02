### Title
Webhook `shop` identifier is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity by HMAC-signing only the raw request body, while the `shop` (tenant) identifier is read from an unsigned HTTP header. An attacker who can obtain one validly-signed webhook body/HMAC pair from *any* shop that uses the app can replay that exact body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `Utils::HmacValidator.validate` will accept the request because it only re-computes the signature over the body, so the app processes attacker-controlled data under a different tenant's identity.

### Finding Description
`Request#to_signable_string` — the value that is HMAC-verified — only returns the raw body: [1](#0-0) 

But `Request#shop`, the value used to identify which merchant/tenant the webhook belongs to, is pulled straight from the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, which is never included in the signed string: [2](#0-1) 

`Registry.process` validates only the HMAC of the body and then blindly trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` calls `verifiable_query.to_signable_string`, i.e. it only proves the *body* bytes were signed with the app's secret — it says nothing about which shop the header claims to be from: [4](#0-3) 

This is precisely the identity-binding break called out by the report: the field the application acts on (`shop`, used as the tenant/session key by the handler) is not the field verified by the HMAC (`raw_body` only). Since Circle... i.e. since the app's `client_secret` used to compute the HMAC is shared across every shop that has the app installed, a valid signature obtained from one shop's webhook traffic is equally "valid" for a forged request claiming to be from any other shop — the signature carries no shop binding at all.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker who operates their own shop with the app installed (an ordinary, unprivileged merchant — no special credentials needed beyond having the app on their own store) can obtain one genuine `(raw_body, hmac)` pair for their own shop (e.g. by pointing a self-registered/custom webhook subscription at infrastructure they control, or observing traffic to their own endpoint if the app is self-hosted and logs it) and then send that same body/HMAC pair to the app's real webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop. The webhook validation logic in `HmacValidator` has no way to detect the tampering because the header was never part of the signed content. The app then processes the attacker's payload as if it originated from the victim tenant — e.g. corrupting the victim's session/mandatory-webhook handling (`shop/redact`, `customers/data_request`, `customers/redact`, `app/uninstalled`) or any custom handler that keys per-tenant state off `data.shop`. This meets the "cross-tenant access" Critical bar.

### Likelihood Explanation
Exploitation requires the attacker to obtain at least one legitimately-signed body for the shared app secret, which any merchant using the app can produce for their own store (webhook events are triggered by ordinary shop actions such as product/order updates, and merchants can direct custom webhook subscriptions to their own observable endpoints via the Admin API if `write_webhooks`/`read_webhooks` scope is granted to their session). No access to the app's `client_secret`, access tokens, or infrastructure is required — this is achievable by any unprivileged internet user who is a merchant of the app.

### Recommendation
Bind the shop identity into the signed material, or otherwise cross-verify it, rather than trusting an unsigned header:
- Include the shop domain (and topic) in `to_signable_string`, if Shopify's webhook signing scheme supports it, or
- After HMAC verification, cross-check `request.shop` against an independently-trusted source (e.g., the shop associated with the stored/expected session or webhook subscription ID) before dispatching to the handler, and reject mismatches.
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key by consuming applications, and add a safer accessor that fails closed when the header cannot be corroborated.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and (using their own session's Admin API access) registers/observes a webhook delivery, capturing a genuine `(raw_body, X-Shopify-Hmac-Sha256)` pair signed with the app's shared `client_secret`.
2. Attacker sends a POST request directly to the app's public webhook endpoint with:
   - Body: the captured `raw_body` (unchanged)
   - Header `X-Shopify-Hmac-Sha256`: the captured, still-valid signature (unchanged)
   - Header `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (changed)
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `raw_body` [1](#0-0)  and succeeds because the body was not modified.
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` [5](#0-4) , even though the payload actually originated from the attacker's own shop, achieving cross-tenant spoofing.

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
