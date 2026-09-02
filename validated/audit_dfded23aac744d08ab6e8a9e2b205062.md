### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) identity fields are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field directly from an unauthenticated HTTP header, while `to_signable_string` — the data that `Utils::HmacValidator` actually verifies — covers only the raw request body. Any party who can obtain one valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key` (e.g. a merchant who has installed the app themselves) can replay that pair to the app's webhook endpoint with an arbitrary, attacker-chosen `X-Shopify-Shop-Domain` header, and the HMAC check will still pass.

### Finding Description
`Webhooks::Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 

But the signable content used for HMAC verification is only the raw body, excluding all headers including `shop`, `topic`, `webhook_id`, and `api_version`: [2](#0-1) 

`Registry.process` validates the HMAC over this signable string and, on success, unconditionally trusts `request.shop` (along with `topic`, `body`, `webhook_id`, `api_version`) when constructing `WebhookMetadata` passed to the host application's handler: [3](#0-2) 

The generic HMAC comparison logic confirms only `verifiable_query.to_signable_string` is signed/verified — nothing header-derived is included: [4](#0-3) 

This breaks the identity binding `authenticated_bytes == fields_acted_upon`. The equality that should hold is:
`HMAC-covered bytes (raw_body) == identity fields consumed by the handler (shop, topic, webhook_id, api_version)`
but in fact only `raw_body` is covered, while `shop` (the tenant key) is taken from a header that travels alongside the body but is not part of the signed payload.

Since Shopify apps use a single `api_secret_key` shared across every shop that installs the app, any merchant with the app installed can legitimately receive a validly-signed webhook (raw body + HMAC) for their own shop. That signed pair remains valid regardless of which `shop-domain` header accompanies it, because the header is never part of the signed content. A malicious merchant can therefore forward that legitimately-signed `(body, hmac)` pair directly to the app's public webhook endpoint while substituting a different shop's domain in the `shop-domain` header, and `HmacValidator.validate` will still return `true`.

### Impact Explanation
This is a cross-tenant identity confusion: the host application processes an attacker-supplied webhook body under the identity of an arbitrary victim shop of the attacker's choosing, because the gem asserts the HMAC "proves" the whole request including `shop`, when it only proves the body. Depending on how host applications key their webhook handling on `data.shop` (typically for locating the tenant's stored session/access token, updating records, or reacting to lifecycle events like `app/uninstalled`), this allows an unprivileged internet user who merely operates their own installed instance of the app to inject falsified webhook events attributed to a different, victim shop — a cross-tenant access impact.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop (a normal, unprivileged action any merchant can take), (2) capturing one webhook delivery `(raw_body, hmac)` for that shop, and (3) POSTing it to the app's public webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key`, access tokens, or any privileged credential is required, since the shared `api_secret_key` is never directly exposed to the attacker — they merely reuse a signature Shopify itself computed for their own webhook.

### Recommendation
Include the tenant-identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable content verified by `HmacValidator`, or otherwise cryptographically bind the `shop` header to the signed body (e.g., by having the host application independently confirm the shop is one for which the app currently holds an active session/access token before trusting `WebhookMetadata#shop`). At minimum, document clearly that `Webhooks::Request#shop`/`#topic`/`#webhook_id` are NOT covered by the HMAC and must not be trusted as tenant identifiers without additional server-side correlation.

### Proof of Concept
1. Attacker installs the vulnerable app on `attacker-shop.myshopify.com` and lets Shopify deliver a legitimate webhook, capturing the raw body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the app's shared `api_secret_key`).
2. Attacker sends a forged HTTP POST directly to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged `shop-domain` header into `#shop`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `@raw_body` (`to_signable_string`) — matching `H` — and passes. [5](#0-4) 
5. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body:, ...)` and processes attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
