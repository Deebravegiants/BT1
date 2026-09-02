## Title
Webhook shop-domain, topic and webhook-id are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

## Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator` verifies binds nothing but the bytes of the body. All identity-carrying values that `Webhooks::Registry.process` subsequently trusts — the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — are read straight from unauthenticated HTTP headers and handed to the app's webhook handler without ever being part of the signed payload.

## Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines: [1](#0-0) 

Specifically: [2](#0-1) 

`to_signable_string` returns `@raw_body` only — no `shop`, `topic`, or `webhook_id` is mixed into the signed string. Yet `Webhooks::Registry.process` trusts these header-derived fields directly after the HMAC check passes: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `to_signable_string`, using the app's single, shared `Context.api_secret_key` (the same secret is used to validate webhooks for *every* shop that has installed the app): [4](#0-3) 

Because the `client_secret`/`api_secret_key` is one shared value across all merchant installations of a multi-tenant app, and only the request body is bound to the signature, a `(raw_body, hmac)` pair legitimately produced for one shop remains valid when replayed with a different `X-Shopify-Shop-Domain` (or `X-Shopify-Topic` / `X-Shopify-Webhook-Id`) header. The equality the gem should enforce — "shop header value == shop bound by the HMAC" — is never checked; the shop identity is accepted purely on the strength of an unauthenticated header.

## Impact Explanation
This breaks the tenant-isolation guarantee that webhook processing is expected to provide: the shop attributed to a webhook event is attacker-controllable independent of whose data actually produced the signed body. An attacker who has their own store installed on the app can:
1. Cause Shopify to emit a legitimately-HMAC-signed webhook body from their own tenant (e.g., by editing a customer/order/product they control, or triggering any subscribed topic), capturing the `raw_body` and its valid `hmac`.
2. Replay that exact `raw_body`+`hmac` to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) to name a victim shop.
3. The app's `HmacValidator.validate` still succeeds (body signature is untouched), and `Registry.process` dispatches the handler with `shop: request.shop` set to the victim's domain and `topic: request.topic` set to whatever the attacker chose.

Depending on how the host application's webhook handlers use `WebhookMetadata#shop`/`#topic` (e.g., updating per-shop state, honoring GDPR `shop/redact`/`customers/redact`, marking a shop as uninstalled on `app/uninstalled`), this allows cross-tenant data corruption, spoofed lifecycle events, or forced data deletion attributed to a shop that never actually sent the event — a cross-tenant boundary violation.

## Likelihood Explanation
Medium. The attacker must be able to install (or otherwise control) at least one shop on the target app to obtain a validly-signed `(body, hmac)` pair, and must be able to make an unauthenticated HTTP POST directly to the app's public webhook endpoint (which by design is a public endpoint, since it must accept unauthenticated Shopify requests). No access token, private key, or credential leak is required — only crafting a header on an otherwise-legitimate signed payload.

## Recommendation
Bind the shop domain (and ideally topic/webhook id) into the value that is HMAC-verified, or independently validate `request.shop` against a value the app trusts out-of-band (e.g., cross-check against a known set of installed shop domains before dispatching), rather than trusting the raw header. At minimum, `to_signable_string` should not be the sole basis for asserting `request.shop`/`request.topic` used downstream in `Registry.process`.

## Proof of Concept
1. App has a single shared `api_secret_key` used to validate all webhooks (`ShopifyAPI::Utils::HmacValidator.validate`, `Context.api_secret_key`).
2. Attacker installs the app on `attacker-shop.myshopify.com` and, through normal use of their own store, triggers a subscribed webhook topic (e.g. `customers/update`) with content they control. Shopify sends:
   ```
   POST /webhooks
   X-Shopify-Topic: customers/update
   X-Shopify-Hmac-Sha256: <valid-hmac-of-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id": 1, "note": "<attacker payload>"}
   ```
3. Attacker captures `Body` and `X-Shopify-Hmac-Sha256` (both valid, signed with the shared secret).
4. Attacker replays:
   ```
   POST /webhooks
   X-Shopify-Topic: customers/update
   X-Shopify-Hmac-Sha256: <same valid hmac>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: {"id": 1, "note": "<attacker payload>"}
   ```
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, because it only checks `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`).
6. The handler is invoked with `WebhookMetadata.new(topic: "customers/update", shop: "victim-shop.myshopify.com", body: {...attacker-controlled...})` (`lib/shopify_api/webhooks/registry.rb:198-199`), despite `victim-shop.myshopify.com` never having sent this event.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
