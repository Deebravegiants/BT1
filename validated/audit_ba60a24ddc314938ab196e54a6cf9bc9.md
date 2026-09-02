This confirms the analog: the gem's documented pattern explicitly tells app developers to use `data.shop` as the tenant/shop identifier (`shop_domain: data.shop` in `docs/usage/webhooks.md:26`), while `data.shop` is populated straight from the `Registry#process` call passing `request.shop`, which is derived from an HTTP header, not from the HMAC-signed payload. [1](#0-0) 

### Title
Webhook `shop` identity used by handlers is not bound by the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then hands the handler a `shop` value read from an HTTP header that is never covered by that signature. This breaks the intended equality `shop authenticated by HMAC == shop delivered to handler`, letting an attacker who controls any one Shopify store using the same app replay a genuinely-signed webhook body while relabeling it as belonging to a different, victim shop.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes and compares the HMAC over `verifiable_query.to_signable_string`. [2](#0-1) 

For webhook requests, `Webhooks::Request#to_signable_string` returns only the raw body — the signed bytes never include the shop domain: [3](#0-2) 

Meanwhile `Webhooks::Request#shop` is read directly from the `X-Shopify-Shop-Domain` / `shopify-shop-domain` header, with no cryptographic tie to the signed body: [4](#0-3) 

`Registry#process` validates only the HMAC and then forwards `request.shop` unchanged to the app's handler as the shop identity for the event: [1](#0-0) 

The gem's own documentation instructs developers to treat `data.shop` as the authoritative tenant identifier for downstream processing (e.g., enqueuing per-shop jobs): [5](#0-4) 

Because the webhook HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared across every shop that installs the app, an unprivileged attacker who installs the app on their own store receives genuine `(body, hmac)` pairs signed with that same secret. Nothing in the signed bytes ties the body to the attacker's own shop domain. The attacker can then POST that same body and HMAC to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` with a victim shop's domain; `HmacValidator.validate` still succeeds (it only checks the body/HMAC pair), and `Registry#process` dispatches the event to the handler labeled as coming from the victim shop.

### Impact Explanation
This breaks tenant isolation: an attacker with no relationship to the victim shop can inject fabricated events attributed to that shop (e.g., fake `orders/create`, `app/uninstalled`, or other topic payloads), causing the app to perform shop-scoped side effects (queued jobs, database writes, business logic) against the victim tenant using attacker-controlled body content. This is a cross-tenant access primitive stemming from an authentication-bypass style identity confusion, matching the Critical impact category (cross-tenant access via a broken identity binding).

### Likelihood Explanation
Likelihood is high for any app author who follows the gem's own documented pattern of trusting `data.shop`/`request.shop` as the tenant key without independently verifying it against the shop that installed the app or against session data. The attacker only needs to install the target app on a store they control (a normal, unprivileged action) to harvest valid `(body, hmac)` pairs, then replay with a spoofed header — no possession of `api_secret_key`, tokens, or victim credentials is required.

### Recommendation
Bind the shop domain into the material that is HMAC-verified, or otherwise cryptographically tie `shop` to the signed payload, rather than trusting a bare header value post-hoc. At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop domain (or the topic/webhook id) so that `HmacValidator.validate` fails if any of these fields are altered independently of the body, and `Registry#process` should cross-check `request.shop` against known/expected shops for the given credentials before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook event (e.g., `orders/create`) on their own store, causing Shopify to POST a body `B` with header `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` and `X-Shopify-Hmac-Sha256: H` computed as `HMAC-SHA256(api_secret_key, B)` — this secret is the single shared `client_secret` for the app across all installs.
3. Attacker captures `(B, H)` at their own callback endpoint.
4. Attacker sends a new HTTP request directly to the app's public webhook endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`. [6](#0-5) 
6. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes/enqueues the attacker's forged body as if it originated from the victim shop.

### Citations

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

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
