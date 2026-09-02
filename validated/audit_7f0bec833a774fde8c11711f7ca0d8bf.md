### Title
Webhook `shop` (and `topic`) identifiers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then hands the handler a `shop` value taken from an HTTP header that is never included in that HMAC computation. This breaks the identity binding `HMAC-verified bytes == bytes the app attributes to a tenant`, allowing a party who can obtain one genuine, validly-signed webhook body (e.g. by installing the app on their own shop) to replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header, causing the handler to process the payload under a victim shop's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` and `topic` accessors are read straight from headers and are not part of the signable string: [2](#0-1) 

`Registry.process` validates the webhook exclusively via `Utils::HmacValidator.validate(request)` — which, per `HmacValidator#validate_signature`, computes the HMAC over `verifiable_query.to_signable_string` (the body only) and compares it to the `hmac-sha256` header. Once that check passes, `request.shop` (attacker-controlled header, uncovered by the signature) is forwarded to the merchant's webhook handler as the trusted tenant identifier: [3](#0-2) [4](#0-3) 

Because the equality that should hold is `HMAC(secret, raw_body) == received_hmac` AND `shop header is bound to that HMAC`, but only the first half is enforced, an attacker who owns any shop that has installed the app can:
1. Receive a genuine webhook delivery from Shopify to their own shop (valid HMAC over that body, computed with the app's real `client_secret`, which the attacker never needs to see).
2. Replay the exact `raw_body` + `hmac-sha256` header value to the app's webhook endpoint, but change the `shopify-shop-domain` (or `x-shopify-shop-domain`) header to a victim shop's domain.
3. `HmacValidator.validate` still succeeds (it never looks at the shop header), and `Registry.process` invokes the handler with `WebhookMetadata#shop` set to the victim's domain while the body content is actually the attacker's own data.

Any handler that uses `data.shop` to select which merchant record to create/update/delete (a very common pattern for `app/uninstalled`, `shop/update`, `orders/*`, etc.) will act on the victim tenant using attacker-supplied data, crossing tenant boundaries.

### Impact Explanation
This is a cross-tenant identity-binding bypass: the app processes webhook payloads under a tenant (`shop`) identity that was never authenticated, only the body bytes were. Depending on what the host app does with `WebhookMetadata#shop` (e.g., marking a shop uninstalled, updating shop-level settings, or storing data keyed by shop), an attacker-controlled shop identity combined with attacker-controlled body content can corrupt or manipulate another merchant's data/state — a cross-tenant access impact.

### Likelihood Explanation
Exploitability requires only that the attacker be able to install the app on a shop they control (a normal unprivileged action for any public/embedded app) and be able to send an HTTP POST to the app's public webhook endpoint with custom headers — no access to `client_secret`, access tokens, or any privileged credential is needed. The vulnerable code path (`Registry.process` / `HmacValidator.validate`) is the gem's documented, standard mechanism for verifying and dispatching webhooks, so any consumer of this library that keys per-tenant logic off `WebhookMetadata#shop` is affected without any misuse of the gem's public API.

### Recommendation
Bind the `shop` (and ideally `topic`) values into the signed material, or otherwise cryptographically tie them to the HMAC:
- Include `shop` and `topic` header values in `Webhooks::Request#to_signable_string` (or a parallel signature/derivation) so the HMAC check fails if these headers are altered independently of the body, or
- Require the host application to additionally verify that `request.shop` matches a shop that this app instance actually has a stored session/access token for before trusting `WebhookMetadata#shop`, and document this requirement clearly since the gem currently gives no such protection.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives (or triggers) a genuine webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (computed by Shopify using the real `client_secret` over `B`).
2. Attacker sends a POST to the app's webhook endpoint with:
   - body = `B`
   - `x-shopify-hmac-sha256` = `H`
   - `x-shopify-shop-domain` = `victim-shop.myshopify.com`
   - `x-shopify-topic` = `orders/create`
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: ...)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation passes.
4. The registered handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., the handler believes this is genuine data for `victim-shop.myshopify.com`, though neither the shop nor topic were ever authenticated. [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
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
