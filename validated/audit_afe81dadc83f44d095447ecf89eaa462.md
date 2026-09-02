### Title
Webhook `shop-domain` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, but the `shop` identity that the app relies on to attribute the webhook to a tenant is taken from an HTTP header that is never included in the signed material. This breaks the equality `shop authenticated (via HMAC) == shop the webhook data is attributed to`.

### Finding Description
`Registry.process` validates authenticity with:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `request.to_signable_string`:
```
def to_signable_string
  @raw_body
end
``` [2](#0-1) 

Meanwhile `shop` (the tenant identity ultimately handed to the app's handler) is read straight from an unauthenticated header:
```
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [3](#0-2) 

`HmacValidator.validate_signature` only compares the computed signature of `to_signable_string` (i.e., `@raw_body`) against the received `hmac` — it never touches the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers:
```
def validate_signature(verifiable_query, secret)
  received_signature = verifiable_query.hmac
  computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
  OpenSSL.secure_compare(computed_signature, T.must(received_signature))
end
``` [4](#0-3) 

Because the signature only binds the body bytes, and not the `shop-domain` header, any request that carries a *previously-valid* `(raw_body, hmac)` pair will pass `HmacValidator.validate` regardless of which `shop-domain` header value accompanies it. The gem then trusts that header value as the tenant identity and forwards it unchanged into `WebhookMetadata#shop`, which is what the host application uses to decide which tenant's data to update/process.

### Impact Explanation
An unprivileged internet user who can install the target app on their own (attacker-controlled) shop — a trivial, unprivileged action available to anyone via the Shopify App Store / dev store — will legitimately receive at least one genuinely-signed webhook `(raw_body, hmac)` pair for their own store. Because the signature never binds `shop-domain`, the attacker can replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` dispatches the handler with `shop: <victim-domain>` and attacker-chosen `body`. Any app logic keyed off `WebhookMetadata#shop` (e.g., "update customer/order/shop data for this shop", GDPR redact processing, billing state, entitlement flags) will now execute attacker-controlled data under another tenant's identity — a cross-tenant integrity/confidentiality violation.

### Likelihood Explanation
Medium-to-High: the prerequisite (installing the app on one's own shop to receive one legitimate signed webhook) requires no privilege beyond normal, unauthenticated app installation, which is the same threat model this scan restricts itself to (unprivileged internet user, no `api_secret_key`/access token needed). No brute force of the HMAC is required — the signature is reused verbatim, only an HTTP header is swapped. Exploitability then depends entirely on how the host app's webhook handler uses `WebhookMetadata#shop`, but the gem itself provides zero protection against this header/body identity mismatch.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`api-version`/`webhook-id`) into the signed material used for verification, or independently verify that the `shop-domain` header matches a shop the app has an active installation/session for before trusting it. At minimum, `Webhooks::Request#to_signable_string` should not be the sole basis for trusting `request.shop`; the registry/handler layer should cross-check `request.shop` against known installed shops before acting on `WebhookMetadata`.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture one legitimate webhook POST, e.g. body `{"id":1}"` with header `x-shopify-hmac-sha256: <valid-hmac-for-body>` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Replay the identical body and HMAC header to the app's webhook endpoint, but replace the header with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` (via `lib/shopify_api/utils/hmac_validator.rb`) succeeds because it only recomputes the HMAC over `raw_body` [2](#0-1) .
4. `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"` and attacker's `body`, as seen in `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, body: request.parsed_body, ...))` [5](#0-4) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
