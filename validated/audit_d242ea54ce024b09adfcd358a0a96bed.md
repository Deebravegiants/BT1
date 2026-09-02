### Title
Webhook HMAC only covers the request body, allowing the `shop`, `topic`, `webhook-id`, and `api-version` headers to be forged while still passing signature validation - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `ShopifyAPI::Utils::HmacValidator.validate` verifies solely that the *body* was signed with `Context.api_secret_key`. The `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers are never included in the signed payload, yet `Registry.process` trusts them verbatim to build the `WebhookMetadata` that is handed to the app's webhook handler.

### Finding Description
`Request#hmac` is read from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header, and `Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`HmacValidator.validate_signature` computes the HMAC purely over `verifiable_query.to_signable_string` (the body) and compares it to the received header: [2](#0-1) 

`Registry.process` then uses `request.shop` and `request.topic` — both unauthenticated header values — to construct the metadata passed to the app's handler: [3](#0-2) 

Because the app's `api_secret_key` is shared across every shop that installs the app (it is not per-shop), any merchant who installs the app can generate a legitimately-signed `(body, hmac)` pair for their own shop's webhook traffic. That pair's validity does not depend on the `shop-domain` header at all — the HMAC identity binding equality that should hold is `hmac == HMAC(secret, body ++ shop ++ topic)`, but the code only enforces `hmac == HMAC(secret, body)`. An attacker can therefore replay a body/hmac pair captured from their own shop's traffic while substituting an arbitrary `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) header pointing at a victim shop, and `HmacValidator.validate` will still return `true`.

### Impact Explanation
This breaks the binding between "the shop whose secret validated the signature" and "the shop the application believes sent the webhook." A handler that uses `WebhookMetadata#shop` to look up a session, update per-tenant records, or drive GDPR/mandatory-webhook flows (`shop/redact`, `customers/redact`, `app/uninstalled`, etc.) can be induced to act on a victim shop's identity using attacker-controlled body content — a cross-tenant confusion inside the gem's own webhook-processing path (`Registry.process`), not merely a downstream app mistake.

### Likelihood Explanation
Exploitation only requires the attacker to be an ordinary (unprivileged) merchant who can install the target app on their own store — no leaked secret, TLS interception, or privileged account is needed. They obtain a valid `(body, hmac)` pair from their own shop's genuine webhook traffic (which they fully control/observe) and resend it directly to the app's public webhook endpoint with a forged `shop-domain` header.

### Recommendation
Include the identity-binding fields in the signed payload used for verification, e.g. bind `shop-domain`, `topic`, and `webhook-id` into `to_signable_string` (or otherwise cryptographically tie the HMAC to those header values) so that a valid signature for one shop/topic cannot be replayed against another. At minimum, document and encourage handlers to independently authenticate the `shop` via a source not derived from the unauthenticated headers before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`), capturing the raw body `B` and the corresponding `x-shopify-hmac-sha256` value `H` from the legitimate delivery (computed by Shopify using the app's single, shop-independent `api_secret_key`).
2. Attacker sends a direct POST to the app's public webhook endpoint with:
   - body `B`
   - `x-shopify-hmac-sha256: H`
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic: orders/create`
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `HmacValidator.validate` recomputes the HMAC over `B` only, which matches `H`, so `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` even though `B`/`H` never originated from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end

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
