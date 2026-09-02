The core issue is in `ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process`: the HMAC signature that authenticates a webhook covers only the raw request body, not the `shop-domain` header that the gem hands to application handlers as the authoritative tenant identifier.

### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-shop webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `ShopifyAPI::Utils::HmacValidator.validate` computes/verifies the HMAC exclusively over that string. The `shop` value (from the `shopify-shop-domain`/`x-shopify-shop-domain` header) is never included in the signed material, yet `ShopifyAPI::Webhooks::Registry.process` forwards it unchanged to the app's webhook handler as the trusted tenant identifier.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
and `HmacValidator.validate_signature` computes the digest solely from `verifiable_query.to_signable_string`: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching, then passes `request.shop` straight into the handler payload without any re-validation against the body or a known registration: [3](#0-2) 

The `shop` accessor simply reads the header verbatim, with no cryptographic binding to the body/HMAC: [4](#0-3) 

The equality this breaks is: `shop-domain header used by the handler == shop that produced (raw_body, HMAC)`. Since `Context.api_secret_key` is a single, app-wide secret (not per-shop) used to validate all shops' webhooks, an attacker who legitimately installs the app on their own store (a fully unprivileged, self-service action) obtains genuine `(raw_body, HMAC)` pairs signed with that same shared secret. The attacker can then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` passes (it never looks at the header), and `Registry.process` calls the handler with `shop:` set to the victim's domain, `body:` set to attacker-controlled content that was never actually issued for that shop.

### Impact Explanation
This is a cross-tenant integrity/confusion issue: a webhook payload can be misattributed to an arbitrary shop that uses the same app, letting a low-privilege attacker (any merchant who installs the app) inject or replay events that host applications trust as coming from a specific victim tenant. Depending on how the host app's handler uses `data.shop` (e.g., to look up records, credit orders, sync data, or key session/storage) this can lead to cross-tenant data corruption or disclosure.

### Likelihood Explanation
Any actor able to install the target app on a store they control (typical for public/self-serve Shopify apps) can capture a valid signed webhook body/HMAC pair for their own shop, since the signing secret (`api_secret_key`) is shared across all shops for that app installation. Forging the header on replay requires no cryptographic secret, no elevated privilege, and no interaction with the victim shop — only network access to the app's public webhook endpoint.

### Recommendation
Bind the shop domain into the signed material (e.g., include `shop-domain` and other identifying headers in the HMAC computation, or independently verify the body's shop-identifying content—such as `X-Shopify-Shop-Domain` combined with body content ids—against a per-registration secret) instead of only signing the raw body while treating the shop header as authoritative and unauthenticated. At minimum, document that `shop` in `WebhookMetadata` is unauthenticated and must be corroborated by the host app before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target Shopify app onto Attacker's own store (`attacker-shop.myshopify.com`), completing OAuth normally.
2. Shopify sends a legitimate webhook (e.g. `orders/create`) to the app's endpoint, signed with the app's shared `api_secret_key`:
   - headers include `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC over raw_body>`.
3. Attacker captures `raw_body` and `x-shopify-hmac-sha256` from that request.
4. Attacker sends a new POST to the same webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which passes because it only checks `raw_body` against the HMAC — see [5](#0-4) .
6. The app's handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, believing it is authentic data for the victim shop.

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
