This confirms the vulnerability. The webhook `Request`'s HMAC only signs `@raw_body` via `to_signable_string` [1](#0-0) , while `shop` is read directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header [2](#0-1) . `Registry.process` verifies only the HMAC of the body and then hands `request.shop` straight to the handler without any cross-check against the signed payload [3](#0-2) .

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw JSON body [1](#0-0) , but the `shop` accessor — which the registry passes to the app's webhook handler as the tenant identifier — is taken from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is never included in the signed bytes [2](#0-1) . `Utils::HmacValidator.validate` only recomputes and compares the HMAC over `to_signable_string` (the body) [4](#0-3) , so the header carrying the shop identity is entirely outside the cryptographic binding.

### Finding Description
The equality that should hold is: `hmac == HMAC(secret, bytes-that-determine-shop)`. In this gem, the bytes that are actually signed are only `@raw_body`, while the shop identity used downstream (`request.shop`, passed into `WebhookMetadata.new(... shop: request.shop ...)`) comes from an unsigned header [5](#0-4) . Because Shopify signs webhooks with the app's single `client_secret` (shared across every shop that has installed the app), a valid `(body, hmac)` pair obtained from a genuine webhook delivered to the app for *any* shop (including one the attacker legitimately controls, e.g., a free/dev store with the app installed) remains cryptographically valid no matter what `shop-domain` header value accompanies it. An attacker who can deliver an HTTP request to the app's webhook endpoint (which is normally internet-reachable, since Shopify calls it over the open internet) can therefore replay a legitimately-signed body while substituting an arbitrary victim `x-shopify-shop-domain` value. `Registry.process` will accept it because `Utils::HmacValidator.validate(request)` only checks the body signature [6](#0-5) , and will then invoke the app's handler believing the event originated from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding: an unprivileged user (an attacker who merely has app-installed access to their own shop) can cause the host application to process attacker-chosen webhook payloads under a spoofed victim `shop` value. Depending on how the host app's webhook handlers use `shop` (e.g., to look up/mutate per-shop records, trigger data deletion for GDPR topics like `customers/redact`, or otherwise act on tenant data), this enables cross-tenant data corruption or disclosure — a boundary the app relies on this gem to enforce.

### Likelihood Explanation
Requires only that the attacker has (or creates) a shop with the target app installed to obtain a genuinely-signed body/HMAC pair, and the ability to send an HTTP request to the app's public webhook endpoint with a modified shop header — both attacker-affordable, unprivileged actions with no access token or `client_secret` needed.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) header values in the signable string, or otherwise cryptographically bind the shop identity to the HMAC-covered payload, so the shop cannot be swapped without invalidating the signature. At minimum, document and/or enforce that host applications must independently verify `request.shop` against a known-installed shop list before trusting it.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook: body `B`, header `x-shopify-hmac-sha256: H` (valid because `H = HMAC(client_secret, B)`), `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker resends the same request to the app's webhook endpoint, keeping body `B` and header `H` unchanged, but replacing `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC only over `B` and matches `H`, so validation passes [6](#0-5) .
4. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [7](#0-6) , causing the app to act on the victim shop's tenant context using attacker-controlled body content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
