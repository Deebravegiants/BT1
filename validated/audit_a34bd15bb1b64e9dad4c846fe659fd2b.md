### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, excluding the `shop-domain` (and `topic`, `webhook-id`, `api-version`) headers from the HMAC-covered data. `ShopifyAPI::Webhooks::Registry.process` validates only that the body's HMAC is correct, then trusts `request.shop` (parsed straight from an attacker-controllable header) as the tenant identity passed to the host application's webhook handler.

### Finding Description
`Utils::HmacValidator.validate` computes/verifies the signature strictly from `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined to return only `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all parsed directly out of caller-supplied HTTP headers, none of which are covered by the signature: [3](#0-2) 

`Registry.process` checks only `Utils::HmacValidator.validate(request)` and then immediately uses `request.shop` as the tenant identity forwarded to the app's handler: [4](#0-3) 

Because every shop that installs the app shares the same `api_secret_key` (a single per-app secret, not per-shop), any merchant/tenant that has legitimately installed the app can trigger a real webhook to their own store, capture the resulting `(raw_body, hmac)` pair, and replay it to the app's webhook endpoint with a forged `shopify-shop-domain` (or `x-shopify-shop-domain`) header pointing at a different, victim shop. The HMAC still validates (it only checks the body against the shared secret), but `WebhookMetadata#shop` — the value the host application uses to resolve per-tenant state/session/handler behavior — now reports the victim's domain instead of the attacker's. This is exactly the "field acted on but not covered by the HMAC" pattern from the report, applied to the identity binding `authenticated_body_owner == claimed_shop`.

### Impact Explanation
This breaks the `shop` binding: the equality that should hold is `hmac_signer_shop == request.shop`, but the gem never checks it — `shop` is out-of-band with respect to the signature. Any of the app's own merchants (an "unprivileged" tenant relative to other tenants) can impersonate a different shop's webhook stream, causing the host application to process attacker-supplied body content under another tenant's identity. Depending on how the host app uses `WebhookMetadata#shop` (e.g., loading that shop's session/access token, updating that shop's local records, triggering mandatory GDPR webhook handlers like `customers/redact` for the wrong shop), this is a cross-tenant confusion primitive reachable purely by an actor who controls (or has ever installed the app on) any single shop.

### Likelihood Explanation
Any developer/merchant who can install the app on their own store can capture a legitimate `(body, hmac)` pair for a topic of their choosing (e.g., by generating that event in their own store) and then send a raw HTTP POST directly to the app's webhook endpoint with a forged `shop-domain` header — no special access, no leaked secrets, and no cooperation from Shopify's real webhook delivery infra is required, since the endpoint is a normal public HTTP route.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`, `api_version`) header values in the signable string used for HMAC verification, or otherwise cryptographically bind the claimed shop to the signed payload, so that a valid HMAC for shop A's body cannot be replayed under shop B's identity. At minimum, document/require verification that `request.shop` matches an already-known, provisioned tenant/session associated with the specific webhook delivery before trusting it in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a legitimate webhook event (e.g. `orders/create`) on their store; Shopify sends `raw_body` and `x-shopify-hmac-sha256` computed with the app's shared `api_secret_key`, plus `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this exact `(raw_body, hmac)` pair.
4. Attacker crafts a new POST to the app's webhook endpoint using the same `raw_body` and `hmac`, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the shared secret [2](#0-1) ; `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: <attacker-controlled/replayed body>, ...)` [5](#0-4) , causing the host app to process attacker data under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
