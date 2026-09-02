Line 125 of `docs/usage/webhooks.md` explicitly states that calling `Registry.process` "will verify the request did indeed come from Shopify" — i.e., the library documents `data.shop` (delivered via `WebhookMetadata`) as a trustworthy, authenticated field. This is the binding the library breaks.

### Title
Webhook shop/topic identity spoofing via HMAC-unsigned headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as fully authenticated ("verify the request did indeed come from Shopify") once `Utils::HmacValidator.validate(request)` passes, and hands `request.shop` and `request.topic` to the app's handler as trusted tenant/topic identifiers. However, the HMAC only signs the raw body; the `shop`, `topic`, `webhook_id`, and `api_version` fields come from unauthenticated HTTP headers and are never included in the signed bytes.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only the HMAC over that body, then forwards the unauthenticated `shop` and `topic` header values to the handler: [3](#0-2) 

The binding the code should enforce but doesn't is: `authenticated(shop_that_generated_HMAC) == shop_delivered_to_handler`. Because the HMAC secret (`api_secret_key`) is a single per-app secret shared across every shop that installs the app (it is not merchant-specific), any merchant who has installed the same app can trigger a legitimate webhook for their own store, capture the resulting `(raw_body, hmac)` pair (which will validate), and replay it to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header naming a different, victim shop. `HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (the body) and compares it via `OpenSSL.secure_compare`: [4](#0-3) 
so the forged headers pass validation unchanged, and `Registry.process` calls the handler believing the payload is authentically attributed to the spoofed shop.

### Impact Explanation
This is a cross-tenant identity break: the app-facing contract documented in `docs/usage/webhooks.md` line 125 promises that `Registry.process` "will verify the request did indeed come from Shopify," implying the delivered `shop`/`topic`/`body` triple is trustworthy as a unit. In reality only the body bytes are authenticated. A handler that uses `data.shop` to attribute the webhook body to a tenant (the documented, expected usage pattern shown in the same doc) can be made to write/act on data for shop B while it was actually a replay of shop A's legitimately-signed webhook, i.e., cross-tenant data confusion/injection using only the attacker's own (legitimately obtained) app installation — no access token, `client_secret`, or privileged account of the victim is required.

### Likelihood Explanation
Any user who can install the target app on their own shop (a normal, unprivileged action) can generate an arbitrary number of legitimately HMAC-signed webhook bodies for topics they control (e.g., `orders/create` in their own store), then POST the captured `(raw_body, hmac)` to the target app's public webhook endpoint with a different `shop-domain` header value. No secret material belonging to the victim or the app is needed by the attacker.

### Recommendation
Bind `shop`, `topic`, `webhook_id`, and `api_version` into the HMAC-covered payload validation logic (e.g., require the receiving application to compare `request.shop` against a shop known to have an active installation/subscription for that specific `webhook_id`/topic pair before trusting it), or update the header contract so `to_signable_string` incorporates these header values, or explicitly correct the documentation to state that only body integrity is verified and callers must independently authorize `shop`/`topic` (e.g., against their own installed-shops list) before use.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (normal merchant flow, no privileged access needed).
2. Attacker triggers a subscribed event (e.g., updates a product) causing Shopify to deliver a webhook to the app's public endpoint with a valid `X-Shopify-Hmac-Sha256` header computed over the raw body using the app's shared `api_secret_key`.
3. Attacker captures that `raw_body` and `X-Shopify-Hmac-Sha256` value (e.g., via their own reverse proxy/logging in front of their webhook receiver, or by running their own copy of the receiving code).
4. Attacker replays the exact same `raw_body` + `X-Shopify-Hmac-Sha256` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and optionally a different `X-Shopify-Topic`).
5. `Utils::HmacValidator.validate` recomputes the HMAC over the unchanged `raw_body` and it matches, so `Registry.process` proceeds and invokes the handler with `WebhookMetadata.new(topic: "victim's topic", shop: "victim-shop.myshopify.com", body: attacker's data, ...)`, causing the host app to process attacker-controlled data as if it were authentic data belonging to `victim-shop.myshopify.com`.

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
