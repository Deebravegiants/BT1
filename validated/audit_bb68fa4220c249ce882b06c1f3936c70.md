## Analysis

The webhook HMAC verification in this gem binds only the **raw request body**, not the Shopify-supplied headers that identify which tenant and event the request represents. This breaks the intended identity binding: `hmac ⇒ (shop, topic, webhook_id, api_version, body)` when in fact `hmac ⇒ (body)` only. [1](#0-0) ### Title
Webhook `shop-domain`/`topic`/`webhook_id` headers are trusted without being covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the **raw body**, but then trusts the `shop-domain`, `topic`, `webhook_id`, and `api_version` values taken from **unsigned HTTP headers** to decide which tenant and event the payload belongs to. This breaks the intended binding `hmac ⇒ (shop, topic, body)`; in the actual implementation `hmac ⇒ (body)` only.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over that signable string: [3](#0-2) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) with no cryptographic linkage to the HMAC: [4](#0-3) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to construct the `WebhookMetadata` passed to the app's handler: [5](#0-4) 

Because the `api_secret_key` used to sign webhooks is the app's single `client_secret` shared across **every shop that installs the app** (not a per-shop secret), any merchant who installs the app receives genuinely-signed webhook deliveries `(body, hmac)` for their own store. Since the HMAC never covers the `shop-domain` header, that merchant (an ordinary, unprivileged actor with no special credentials) can capture one of their own valid `(raw_body, hmac)` pairs and resubmit it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop's domain (and/or the `shopify-topic`/`shopify-webhook-id` headers altered). `HmacValidator.validate` still succeeds because the body is unchanged, and `Registry.process` hands the handler a `WebhookMetadata` claiming the data originated from the victim shop.

This is precisely the bug class described in the report: a value that is *acted upon* (the shop identity used to route/attribute webhook data) is not covered by the same integrity check (`HMAC`) that authenticates the request, letting the caller substitute unauthenticated data for the value the rest of the system relies on for a security decision.

### Impact Explanation
This crosses the tenant boundary invoked in the rules ("cross-tenant access", Critical). Any application built on this gem's documented `Registry.process` API and `WebhookHandler` contract will process a spoofed shop identity as if it came from Shopify. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to persist data, invalidate caches, dispatch cross-tenant operations, or as a lookup key for tenant-scoped session/config), an attacker-controlled merchant can inject attacker-influenced data attributed to a victim tenant, potentially corrupting or exfiltrating data associated with a shop they do not own or control — without needing the app's `client_secret`, an access token, or any elevated privilege beyond being able to install the app on their own (attacker-owned) shop.

### Likelihood Explanation
Likelihood is high relative to the report's own "High difficulty / requires oracle malfunction" baseline, because no external malfunction is required here — only normal, expected use of the gem's public webhook endpoint. Any user capable of installing the app on a shop they control can trivially capture legitimately-signed webhook payloads and replay them with modified headers; no cryptographic material needs to be broken or guessed since the header fields were never included in the signed payload in the first place.

### Recommendation
- Bind the routing/attribution fields into the signed payload verification: include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or otherwise cryptographically bind them, e.g., via a MAC that also covers these header values), so a valid HMAC can only be produced for the exact `(shop, topic, webhook_id, body)` tuple actually sent by Shopify.
- Short term, at minimum, document/enforce that the host application must independently verify the `shop` returned by `WebhookMetadata` against a known, previously-registered shop for that specific webhook subscription (e.g., cross-check `webhook_id` against the ID returned when the app registered the topic for that shop) rather than trusting the header value directly.
- Long term, follow the same "explicit caller-supplied binding" principle from the source report: require verification to be performed against an expected/allow-listed shop for the given webhook subscription id rather than inferring shop identity from an unauthenticated header.

### Proof of Concept
1. App developer installs their app on `attacker-shop.myshopify.com` (a normal, permission-less installation).
2. Attacker triggers an event (e.g., creates a product) causing Shopify to send a legitimately-signed webhook to the app's endpoint:
   - Headers: `shopify-shop-domain: attacker-shop.myshopify.com`, `shopify-topic: products/create`, `shopify-hmac-sha256: <valid HMAC over body>`
   - Body: attacker-controlled product JSON (attacker can shape most of its content by choosing product attributes).
3. Attacker intercepts/replays this exact `(raw_body, hmac)` pair to the same app endpoint, but rewrites the header:
   - `shopify-shop-domain: victim-shop.myshopify.com`
4. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC: [6](#0-5) 
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "products/create", body: <attacker JSON>, ...)`, and the host application acts on data it believes came from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-10)
```ruby
      sig { override.returns(String) }
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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
