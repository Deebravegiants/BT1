### Title
Webhook `shop`, `topic`, and `webhook_id` headers are trusted by the handler but excluded from the HMAC-verified byte range - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates only the raw request body via HMAC, then forwards the `shop`, `topic`, `webhook_id`, and `api_version` header values — none of which are covered by that HMAC — to the app's handler as authoritative tenant/event identity. This is the exact bug class from the external report: one piece of state (`premiumCollected`) is bound into a protected computation (token price), while a related piece of state that is *acted on* (`performanceFee`) is not, letting an actor manipulate the unprotected side to shift value. Here, the "protected computation" is `HmacValidator.validate`, and the "acted on but unprotected" field is the `shop`/`topic`/`webhook_id` header set that downstream handlers rely on to key their side effects (e.g., "which merchant does this event belong to").

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes the HMAC exclusively over that signable string and compares it to the `hmac-sha256` header: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read straight from HTTP headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` validates only the HMAC, then passes the unauthenticated `request.shop`/`request.topic`/`request.webhook_id` straight into `WebhookMetadata`, which the app's handler treats as ground truth for which tenant the event belongs to: [4](#0-3) [5](#0-4) 

The identity equality that should hold is: `HMAC-covered bytes == bytes the handler uses to determine tenant/event identity`. Instead, `HMAC-covered bytes == raw_body only`, while `tenant/event identity used by handler == headers (shop, topic, webhook_id)`. Because the `api_secret_key` used to sign webhook bodies is shared across every shop that has this specific app installed (it's an app-level, not shop-level, secret), a valid HMAC over a given body proves only "this body was produced by Shopify for *some* installation of this app" — it proves nothing about *which* shop the event is for. Any party who can obtain one genuinely Shopify-signed `(body, hmac)` pair for the app (trivially available to anyone who installs the app on their own store, which requires no `api_secret_key`, access token, or privileged account) can replay that exact body/HMAC pair while substituting an arbitrary `X-Shopify-Shop-Domain` (and `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header, and `HmacValidator.validate` will still pass — because those headers were never part of what was signed.

### Impact Explanation
This breaks the tenant boundary that this gem's webhook processing is supposed to enforce: `Registry.process` is documented as verifying "the request did indeed come from Shopify" before invoking the handler for "that webhook" (docs/usage/webhooks.md), implying that `data.shop` in `WebhookMetadata` can be trusted as the shop the event pertains to. In practice an attacker who legitimately installs the target app on their own store (an ordinary, unprivileged action) can capture a real signed webhook delivery and replay it against the app's public webhook endpoint with a forged `shop-domain` header naming a victim shop. Any host application that uses `data.shop` to look up/write per-tenant records, revoke access, process GDPR/mandatory webhooks (`app/uninstalled`, `shop/redact`, `customers/data_request`), or gate business logic per merchant will act on attacker-supplied data attributed to a victim tenant it never actually came from — i.e., cross-tenant impersonation without needing the app's `client_secret`, an access token, or any credential belonging to the victim.

### Likelihood Explanation
Likelihood is meaningful but bounded: the attacker must (a) be able to install the app on some shop (ordinary, unprivileged), (b) capture one of the app's genuine webhook deliveries for that shop (trivial — it's their own inbox/log), and (c) send a forged HTTP request to the app's publicly reachable webhook endpoint with the same body/HMAC but a different `shop-domain`/`topic` header. No secret material or elevated privilege is required at any step, and the gem itself provides no header binding to prevent it — the mitigation would have to live in the host application (e.g., cross-checking `shop` against something signed), which the gem does not do or document as necessary.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the bytes covered by the HMAC comparison (or otherwise cryptographically bind them to the body before trusting them), analogous to fixing the smart-contract bug by folding the unbound `performanceFee` into the same accounting as `premiumCollected`. Concretely, `Request#to_signable_string` should incorporate the header values that `Registry.process`/`WebhookMetadata` treat as authoritative, or `Registry.process` should independently verify that the `shop` header corresponds to a shop the app actually has a webhook registration/session for before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (no special privilege needed) and subscribes to a webhook topic whose delivery to the app's endpoint they can observe (e.g., via their own server logs), capturing the raw POST body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify using the app's `api_secret_key`, which the attacker never sees but which is the same for every shop using this app).
2. Attacker sends a new POST to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid per [2](#0-1) ), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and any `X-Shopify-Topic`/`X-Shopify-Webhook-Id` of their choosing.
3. `ShopifyAPI::Webhooks::Request.new` accepts this (only checks header presence, not header authenticity) per [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, since only `B` is checked — then invokes the app's handler with `shop: "victim-shop.myshopify.com"`, per [7](#0-6) .
5. The host app processes body `B` (attacker-chosen event data from their own shop's real webhook) as if it belongs to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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
