## Title
Webhook shop/topic identity spoofing via cross-tenant HMAC replay — HMAC binds only the raw body, not the `shop-domain`/`topic`/`webhook_id` headers used to route and attribute the webhook - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authorizes an inbound webhook solely by validating an HMAC computed over the raw request body, then dispatches to a handler using `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers that are **not covered by that HMAC**. Because the app's webhook signing secret (`Context.api_secret_key`) is a single shared secret used for every shop that installs the app, any merchant who legitimately installs the app can obtain a genuinely-signed `(body, hmac)` pair for their own shop and then replay it to the app's public webhook endpoint with the `shop-domain`/`topic`/`webhook_id` headers rewritten to name a different (victim) shop or a more sensitive topic (e.g. `app/uninstalled`, `shop/redact`). The library will treat the payload as authentic and dispatch it under the attacker-chosen shop/topic identity.

### Finding Description
The webhook signature check is: [1](#0-0) 

Specifically, `hmac` is read from the header and `to_signable_string` returns **only** `@raw_body`: [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from headers with no cryptographic binding: [3](#0-2) 

`HmacValidator.validate` confirms only that the body's HMAC matches (using the single shared `Context.api_secret_key`, identical across all shops that install this app): [4](#0-3) 

`Registry.process` then trusts the unauthenticated headers to select the handler and to build the metadata passed to it: [5](#0-4) 

The equality that should hold but does not: `shop` (and `topic`) *authenticated by the HMAC* == `shop`/`topic` *acted upon by the handler*. In reality: `HMAC(body)` binds nothing but `body`; `shop`, `topic`, `webhook_id` are attacker-controlled headers that flow unchecked into `WebhookMetadata` and into handler dispatch (`@registry[request.topic]`).

### Impact Explanation
An attacker who installs the app on their own shop (an ordinary, unprivileged tenant — no `api_secret_key`, no stolen token, no TLS interception needed) will receive real webhooks from Shopify for their own store, each with a valid `(body, hmac)` pair signed with the app's single shared secret. Because many webhook topics have small/predictable or attacker-influenceable bodies (or the attacker can trigger topics whose payload they control, e.g. by editing their own store's resources), they can obtain a valid `hmac` for a chosen body. They then POST that exact `body` + `hmac` to the app's public webhook endpoint while setting `x-shopify-shop-domain` to a victim shop and `x-shopify-topic`/`x-shopify-webhook-id` to a sensitive topic such as `app/uninstalled` or a GDPR `shop/redact` topic. `Utils::HmacValidator.validate` passes (only the body is checked), and the handler executes cross-tenant logic (e.g. deleting the victim's stored session/access token, purging victim data, or any app-specific uninstall/redaction side effect) attributed to the victim shop. This is a cross-tenant action triggered without any credential belonging to the victim, satisfying the Critical "cross-tenant access" impact bar.

### Likelihood Explanation
Likelihood is realistic for any app exposing webhook handlers for topics with attacker-influenceable or low-entropy bodies (common for lifecycle topics like `app/uninstalled`, or metafield/tag topics where the attacker controls their own store's data). The attacker requires no special privilege beyond installing the target app on their own store — a normal, unprivileged action available to any internet user who can install a public Shopify app.

### Recommendation
Bind the identity fields into the signed payload check, e.g. include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically tie the header values to the request, e.g. by deriving them only from a payload structure Shopify signs as a whole), and/or require the caller to supply/verify the expected shop out-of-band (e.g. compare `request.shop` against the shop of the session/store the handler is invoked for) rather than trusting the header outright once body-HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. `POST /webhooks` with body `{}` and header `x-shopify-hmac-sha256: <valid-hmac-of-"{}">` (many topics/bodies are minimal/predictable — the shared HMAC key is the app-wide secret, not shop-specific).
2. Attacker replays the same request to the app's public webhook endpoint but rewrites headers:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - `x-shopify-topic: app/uninstalled` (or another sensitive topic whose handler is registered and whose triggering body is `{}`/predictable)
   - keeps the original body `{}` and the original valid `x-shopify-hmac-sha256`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(raw_body)` — see [6](#0-5) .
4. The registered handler for `app/uninstalled` is invoked with `shop: "victim-shop.myshopify.com"` (from the spoofed header), performing uninstall/cleanup logic for the victim tenant that the attacker never authenticated for.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
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

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
