Confirmed. `Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `HmacValidator.validate` only authenticates the request body bytes, never the `shop`, `topic`, `api_version`, or `webhook_id` headers [2](#0-1) . `Registry.process` accepts any request whose body HMAC checks out and then trusts `request.shop`/`request.topic` taken straight from unauthenticated headers to build the `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Title
Webhook `shop`/`topic` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing via replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `Utils::HmacValidator` signs/verifies solely that string. The `shop`, `topic`, `api_version`, and `webhook_id` values are read straight from HTTP headers and are never part of the signed payload, yet `Registry.process` treats a passing HMAC check as proof that the entire request — including `shop` — is authentic and hands it to the app's `WebhookHandler`.

### Finding Description
The binding the gem is supposed to enforce is: `hmac(raw_body, api_secret_key) valid` ⇒ "this entire webhook, including which shop it is for, was sent by Shopify for this shop". In reality the equality only holds for the body bytes:

- `to_signable_string` = `@raw_body` only [4](#0-3) .
- `HmacValidator.validate_signature` computes `HMAC-SHA256(secret, to_signable_string)` and compares it against the `hmac` header [2](#0-1) .
- `shop`, `topic`, `api_version`, and `webhook_id` are parsed from headers with no cryptographic binding to the body or to each other [5](#0-4) .
- `Registry.process` only checks `Utils::HmacValidator.validate(request)` and then immediately trusts `request.shop`/`request.topic` to look up the handler and build `WebhookMetadata` [3](#0-2) .

An unprivileged internet user who operates their own Shopify development store receives genuine, correctly-signed webhooks for their own shop (this requires no privileged Shopify credentials — any developer can spin up a free dev store and register a webhook). Because the signature covers only the body, that same `(raw_body, hmac)` pair remains valid no matter what `shopify-shop-domain` or `shopify-topic` header value accompanies it. The attacker can replay the captured body+HMAC pair to the target app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header (e.g., a victim merchant's domain) and/or a different `shopify-topic`. `Registry.process` passes HMAC validation and dispatches `WebhookMetadata.new(shop: <attacker-chosen>, topic: <attacker-chosen>, ...)` to the app's handler as if it were an authentic event for that shop/topic.

### Impact Explanation
This breaks the tenant-identity binding between the cryptographically verified bytes and the `shop`/`topic` fields the host application relies on to route data per-tenant. Any app that uses `WebhookMetadata#shop` (the value the gem itself exposes as "the shop this webhook is for") to key persistence, cache invalidation, entitlement checks, or redaction logic (e.g., `customers/redact`, `shop/redact`) can be made to apply attacker-controlled body content to a different (victim) shop's tenant record, since the gem provides no signal that `shop` was unauthenticated. This is a cross-tenant data-integrity/isolation break attributable to the gem's own webhook verification API, not a documented limitation the host app is expected to work around — the gem does not document that only the body is authenticated, and `HmacValidator`/`Registry.process` are presented as the complete verification mechanism.

### Likelihood Explanation
Likelihood is realistic: obtaining a valid `(body, hmac)` pair requires only owning any Shopify store (free/dev stores are trivially obtainable) and registering a webhook to an endpoint you control to capture a legitimate payload, then replaying it to the victim app's public webhook URL with modified headers — no access token, `client_secret`, or privileged account is required.

### Recommendation
Include `shop`, `topic`, and any other header fields the application will trust in the signable string used for HMAC verification, or independently authenticate the shop domain against session/OAuth state before dispatching `WebhookMetadata` to handlers. At minimum, document clearly that `HmacValidator` only authenticates the raw body and that `shop`/`topic` headers must be independently corroborated (e.g., against a known list of installed shops) before being trusted as tenant identifiers.

### Proof of Concept
1. Attacker installs their own app-development store (`attacker.myshopify.com`) and registers a webhook for `customers/data_request` pointing at a URL they control, capturing the raw POST body `B` and the `x-shopify-hmac-sha256` header `H` that Shopify sends (valid because `H = HMAC(secret, B)`).
2. Attacker sends a POST to the victim app's real webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), but `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`).
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)` [6](#0-5)  which passes because it only hashes `B`.
4. The app's handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` [7](#0-6)  and processes attacker-supplied body content as if it were authentic data for `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
