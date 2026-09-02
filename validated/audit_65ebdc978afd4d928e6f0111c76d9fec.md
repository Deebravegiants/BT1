## Finding [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verified in `Registry.process` authenticates the body bytes but never binds the `shopify-shop-domain` header that is later trusted as the tenant identity for the webhook. This is the same class of bug as the reported `BlockhashRegistry` issue: a value used to establish a trust chain (there, the parent hash; here, the `shop`) is accepted without being covered by the check that is supposed to guarantee its authenticity.

### Finding Description
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable content from the raw body alone:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers, independent of the signed content:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [4](#0-3) 

`Registry.process` validates the HMAC over `request` (i.e., over `@raw_body` only, via `HmacValidator.validate`) and then immediately trusts `request.shop` as the tenant identity handed to the app's webhook handler:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

`HmacValidator.validate` confirms this: it only ever signs/compares `verifiable_query.to_signable_string`, which for a webhook `Request` is `@raw_body`:
```ruby
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [5](#0-4) 

The equality that should hold is: `shop delivered to handler == shop that Shopify actually attributes to the signed body`. Because the header is outside the signed scope, that equality is never enforced — the gem breaks it by construction.

### Impact Explanation
Any Shopify merchant (an "unprivileged internet user" with respect to this app — no `api_secret_key`, no access token, no privileged account required) can install the target app on their own store and legitimately receive genuine, correctly-signed webhooks (body + HMAC) from Shopify. Because the HMAC only covers `@raw_body`, that exact `(body, hmac)` pair remains valid for *any* `shop-domain` header value. The attacker can replay the captured request to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain (publicly known, e.g. `victim-shop.myshopify.com`). `HmacValidator.validate` still succeeds (it never inspects the header), and `Registry.process` hands the handler `shop: "victim-shop.myshopify.com"` together with attacker-controlled `body`. Any host application logic that keys off `data.shop` (e.g., updating shop-scoped records, honoring `app/uninstalled` to clear a victim's session, acting on `customers/redact` or `shop/redact` GDPR topics, or writing order/product data under the victim's tenant) is now cross-tenant confusable — the classic "shop authenticated versus shop acted upon" binding break called out in scope.

### Likelihood Explanation
Exploitation only requires a free/trial Shopify store (no leaked credentials, no TLS interception, no social engineering) and knowledge of a victim's myshopify domain, which is typically public. The library gives no built-in protection against this replay because the signable string never contains the shop identity, so any application relying on the gem's `Registry.process`/`WebhookMetadata` for tenant attribution is affected by default.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is HMAC-verified, or otherwise fail closed when the header-derived shop cannot be corroborated. Concretely, `Request#to_signable_string` should incorporate the same shop value Shopify signed, or `Registry.process` should independently verify `request.shop` (e.g., against `Utils::ShopValidator.sanitize!` and the set of shops with an active/known session) before invoking the handler. At minimum, document — and preferably enforce in `Registry.process` — that `WebhookMetadata#shop` must not be treated as fully authenticated to tenant-scoped actions without an additional lookup keyed on a separately signed value.

### Proof of Concept
1. Attacker installs the target app on their own real store `attacker.myshopify.com` and triggers a webhook topic the app subscribes to (e.g., `orders/create`), causing Shopify to POST a legitimately HMAC-signed body to the app's webhook endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures the raw POST body and the `x-shopify-hmac-sha256` header value from this request.
3. Attacker resends the identical body/HMAC to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only [5](#0-4)  — it matches, so validation succeeds.
5. `Registry.process` dispatches to the handler with `shop: "victim-shop.myshopify.com"` and the attacker's own body content [3](#0-2) , causing the host app to process attacker-controlled data under the victim's tenant identity.

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
