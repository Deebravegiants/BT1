### Title
Webhook Shop Identity Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats an incoming webhook as authentic once its HMAC validates, then hands the handler a `shop` value taken directly from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header. The HMAC computed by `ShopifyAPI::Webhooks::Request#to_signable_string` binds only the raw request body — never the shop, topic, webhook-id, or api-version headers — so any bytes that produce a valid signature for one shop's payload can be replayed with a different shop header and will still pass verification.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature purely from `to_signable_string` and compares it to the supplied `hmac`: [2](#0-1) 

`Registry.process` treats a passing HMAC check as proof the whole request — including `shop`, `topic`, `webhook_id`, and `api_version`, all of which are read straight from headers — is authentic, and forwards them unchanged to the app's handler: [3](#0-2) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all sourced from headers that are never part of the signed content: [4](#0-3) 

The identity binding that should hold is: `shop asserted to the handler == shop the merchant/HMAC-secret owner actually intended to identify`. Because the signature only certifies the body bytes, this equality is never enforced — the `shop` header is fully attacker-controllable independent of the HMAC. Since a single app's `client_secret`/`api_secret_key` is shared across every shop that installs the app, any holder of a valid `(body, hmac)` pair for shop A (which they can trivially obtain by installing the app on their own store and receiving a real webhook) can resend that exact body/hmac to the app's webhook endpoint with the `shop-domain` header rewritten to victim shop B. `Registry.process` will accept it as a legitimate webhook for shop B, because the HMAC check passes and nothing else is verified.

This mirrors the reported bug class: one entry point (`withdraw`) enforces a check while a semantically equivalent entry point (`decreaseLiquidity`) skips it because the check wasn't bound to all paths that expose the sensitive action. Here, the "checked" content (body) and the "acted-on" content (shop identity used for tenant routing) are decoupled — the field the handler acts on (`shop`) is not covered by the same cryptographic guarantee that gates processing.

### Impact Explanation
Any app relying on `WebhookMetadata#shop` (as documented in `docs/usage/webhooks.md`) to key per-tenant state (e.g., "update order/inventory record for shop X") can be made to apply attacker-supplied but HMAC-"verified" webhook bodies against an arbitrary victim shop, since the shop identity is never bound to the signature. This is cross-tenant data confusion/corruption driven entirely through this gem's own webhook validation contract, not through host-app misuse — the gem itself asserts an authenticated `shop` field that in fact carries no such guarantee.

### Likelihood Explanation
Exploitation only requires that the attacker be able to install the target app on at least one shop they control (to obtain a valid signed payload) and be able to send an HTTP request to the app's public webhook callback endpoint with a modified `shop-domain` header — no access token, secret, or privileged account is needed beyond ordinary merchant self-service app installation.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed payload verification, or otherwise cryptographically bind the `shop` header to the credential context before exposing it to `WebhookMetadata`, so that a validated HMAC actually certifies the tenant identity being acted upon, not just the raw body bytes.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic and capture the resulting request: `raw_body`, and header `x-shopify-hmac-sha256` (valid for that body under the app's shared `api_secret_key`).
2. Replay the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` (called from `Registry.process`) only checks the body against the HMAC, so it returns `true`. [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.shop == "victim.myshopify.com"`, even though the payload was never actually generated or authorized for that shop.

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
