This confirms the vulnerability. The `Utils::HmacValidator.validate(request)` call in `Registry.process` only verifies the HMAC against `request.to_signable_string`, which is defined as `@raw_body` alone. The `shop`, `topic`, `webhook_id`, and `api_version` values are all read from HTTP headers that are never included in the signed content, yet `Registry.process` trusts `request.shop` and passes it directly into `WebhookMetadata` for the handler to act on.Now I have full confirmation of the vulnerable path. Here is the finding.

### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating an HMAC over the raw request body only, then unconditionally trusts the `shop-domain` (and `topic`, `webhook-id`, `api-version`) HTTP header values, which are not part of the signed content, and hands them to the app's `WebhookHandler` as the tenant identity for that payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from HTTP headers that are never fed into the signature computation: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body) and compares it against the `hmac-sha256` header: [3](#0-2) 

`Registry.process` calls this validator, and — on success — immediately trusts `request.shop` (the unauthenticated header) as the tenant identity, packaging it into `WebhookMetadata` that is delivered to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop` == "the shop the signed `raw_body` actually originated from". Instead the gem only proves "the raw body was signed with our `api_secret_key`" and separately trusts an arbitrary, unauthenticated header for which shop that body belongs to. Because the same `api_secret_key` is shared across every shop that installs the app, any legitimate webhook the app receives for **any** shop (including one an attacker fully controls, e.g. a shop they installed the app on themselves) produces a validly-signed `raw_body` + `hmac-sha256` pair. An attacker who controls this pair can then replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim's shop domain. `HmacValidator.validate` still succeeds (it never looked at the header), and `Registry.process` passes the victim's domain to the handler alongside the attacker's own webhook body/topic.

### Impact Explanation
This breaks the shop-authenticated-versus-shop-acted-upon identity binding described in the rules, enabling cross-tenant confusion: a handler that uses `WebhookMetadata#shop` to select which merchant's stored access token/session to act on (a common and gem-documented pattern, see `docs/usage/webhooks.md`) will perform writes/side effects or trigger authenticated Admin API calls against the victim shop using attacker-supplied body content, since the *only* thing verified is that some shop's data was signed by the shared app secret, not that it was signed *for* the shop claimed in the header. This is a cross-tenant access issue reachable by any user who can install the app on their own store (unprivileged) and does not require the `api_secret_key`, an access token, or any privileged credentials.

### Likelihood Explanation
High reachability: any merchant/attacker who installs the app receives real webhooks for topics they subscribed to, giving them a validly-signed `raw_body`/`hmac-sha256` pair "for free" without needing the secret. Replaying that pair to the same public HTTP endpoint with a spoofed `x-shopify-shop-domain` header is a trivial HTTP replay requiring no cryptography, since header values are completely outside the HMAC's scope.

### Recommendation
Bind the shop identity cryptographically into the verified content, or independently verify header-derived fields (`shop`, `topic`) against data embedded in/derivable from the signed body, or require the host app to only ever act on `WebhookMetadata#shop` after separately confirming it corresponds to a shop with a known, previously-established install/session — never trust `x-shopify-shop-domain` as sole tenant identity for a payload whose HMAC does not cover it. At minimum, document in `docs/usage/webhooks.md` that `shop`, `topic`, `api_version`, and `webhook_id` are NOT covered by the HMAC and must not be trusted as tenant-binding without additional verification.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and subscribes to a webhook topic (e.g. `orders/create`).
2. Shopify sends the attacker a webhook: raw body `B` plus header `x-shopify-hmac-sha256: H` (valid, computed by Shopify using the app's `api_secret_key`) and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `B` and `H`, then POSTs to the app's public webhook endpoint with the same body `B` and the same `hmac-sha256` header `H`, but rewrites the header to `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` is constructed; `Utils::HmacValidator.validate(request)` succeeds because it only recomputes HMAC over `B`.
5. `Registry.process` looks up the handler for the topic and invokes `handler.handle(data: WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...))`, causing the app to process attacker-controlled body content under the victim shop's identity.

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
