### Title
Webhook shop domain not covered by HMAC allows cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/utils/hmac_validator.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, but the `shop` (and `topic`/`webhook_id`) values that are subsequently trusted and handed to the app's webhook handler come from unauthenticated HTTP headers that are never part of the signed content. This breaks the intended binding: *shop authenticated by HMAC* should equal *shop acted upon by the handler*, but here the HMAC only proves the body originated from an app-secret holder for **some** shop — not the shop named in the header.

### Finding Description
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.), with no cryptographic binding to those values: [1](#0-0) 

Its `to_signable_string` — the thing the HMAC is actually computed over — returns only `@raw_body`: [2](#0-1) 

`HmacValidator.validate` computes `HMAC-SHA256(client_secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field, i.e. it validates only the body bytes, never the header-derived `shop`/`topic`/`webhook_id`: [3](#0-2) 

`Registry.process` then trusts `request.shop` (and `request.topic`, `request.webhook_id`) as authenticated tenant identity and forwards them straight to the app's handler: [4](#0-3) 

`WebhookMetadata.shop` is a plain `String` field with no further validation, and the gem's own documentation instructs integrators to use `data.shop` as the tenant identifier for follow-on actions (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [5](#0-4) 

Because Shopify's app-level `client_secret` used to compute webhook HMACs is the same secret across **every** shop that has installed the app, an attacker who has installed the app on their own (unprivileged) shop can:
1. Trigger a webhook to their own store with attacker-controlled body content, obtaining a genuinely-signed `(raw_body, hmac)` pair computed with the app's shared `client_secret`.
2. Replay that exact body and HMAC to the app's public webhook endpoint, but with the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header rewritten to point at a **victim** shop.
3. `HmacValidator.validate` passes, because the HMAC is only a function of `raw_body`, which was not modified. `Registry.process` calls the handler with `shop: <victim-shop>` and `body: <attacker-controlled JSON>`.

The equality the gem should enforce — *the shop whose secret produced this HMAC == the shop the handler is told to act on* — does not hold, because the shop identity is carried in an unsigned header while only the body is signed.

### Impact Explanation
This is a cross-tenant identity-binding break: an unprivileged internet user (any developer who can install the public app on their own free/dev store) can forge webhook events that the host application will process under the identity of a completely different, victim shop, with attacker-chosen body content (for topics like `orders/create`, `customers/update`, etc., whose payload content is largely determined by the attacker's own store data). Any downstream logic keyed off `WebhookMetadata#shop` (as the gem's own docs recommend) — enqueuing background jobs scoped to a shop, updating per-shop records, looking up a shop's stored `access_token` by shop domain, etc. — will operate against the wrong tenant using attacker-supplied data. This matches the "Critical - cross-tenant access" impact category, since it lets one tenant inject data/events attributed to another tenant without ever presenting that tenant's credentials.

### Likelihood Explanation
No privileged access, leaked secret, or social engineering is required — only the ability to install the app on any Shopify store (a normal unprivileged action available to anyone) and to send a crafted HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header. The gem performs no check that the header-derived shop matches anything cryptographically related to the signed body, so exploitation is a matter of capturing one's own legitimate webhook and replaying it with a different header value.

### Recommendation
Bind the shop (and ideally topic/webhook_id) identity into the HMAC-verified content, or otherwise re-derive/verify it independently of the client-supplied header:
- Include `shop`, `topic`, and `webhook_id` in the signable string used for HMAC verification (this would require Shopify to sign a canonical string including these values — verify against Shopify's actual signing behavior before changing the signable string, since Shopify currently only signs the raw body).
- Failing that, require the host application (and document prominently) to independently validate that the shop named in `x-shopify-shop-domain` is one of its currently-installed shops for which this webhook `topic`/`webhook_id` combination is registered, rather than trusting the header at face value as an authenticated identity.
- At minimum, add explicit documentation/warning in `docs/usage/webhooks.md` and on `WebhookMetadata#shop` that this field is **not** cryptographically authenticated and must not be used as a sole tenant-scoping key without additional server-side verification (e.g., cross-checking against the shop for which the app registered this specific `webhook_id`).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (a shop they own), obtaining webhook delivery to the app's `/callback/orders/create` endpoint for real Shopify-generated events signed with the app's shared `client_secret`.
2. Attacker triggers an `orders/create` event on their own store with an order payload they fully control (attacker sets order fields, e.g. `note`, `email`, custom line items) and captures the raw POST body `B` and the resulting `x-shopify-hmac-sha256` header `H = HMAC-SHA256(client_secret, B)`.
3. Attacker sends a new POST directly to the app's public webhook endpoint:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: H
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: <any>
   x-shopify-api-version: 2024-01

   <body B>
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because `to_signable_string` returns only `B`, unaffected by the header change (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. The app's handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's parsed JSON>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-controlled data as though it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
