### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are trusted from unauthenticated headers, not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request **body**, then dispatches to the handler using `shop`, `topic`, `webhook_id`, and `api_version` values that are read straight from HTTP headers and are never part of the signed material.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled directly from attacker-controllable headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC (i.e., only the body) via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`WebhookMetadata.shop` is a plain `String` field with no further validation performed by the gem: [4](#0-3) 

The identity binding that is broken is: `HMAC-authenticated bytes == raw_body only`, while `bytes acted upon (shop, topic, webhook_id) != raw_body`. Because Shopify's real HMAC computation for webhooks is over the body exclusively (this is expected/documented Shopify behavior, not a bug in this gem's crypto), any entity capable of producing a body with a **valid HMAC for some shop** (e.g., a merchant who owns their own store and receives genuine webhooks with a valid `X-Shopify-Hmac-Sha256` for a JSON body they know) can replay that exact `(body, hmac)` pair while substituting an arbitrary `X-Shopify-Shop-Domain` header pointing at a different tenant. `Registry.process` will accept it as valid ("Invalid webhook HMAC" check passes since it only checks the body) and hand the handler a `WebhookMetadata` whose `shop` field claims to be a different merchant than the one that actually sent/owns the payload.

This matches the class of "field acted on but not covered by the HMAC" identity-binding break described in the analog rules: the gem authenticates bytes (`raw_body`) but then acts on a different field (`shop`) that was never part of what was authenticated.

### Impact Explanation
If a host application's webhook handler uses `WebhookMetadata#shop` to select which tenant's data/session to mutate (a normal and encouraged pattern, since the whole purpose of `shop` is to identify which store the event belongs to), an attacker who can obtain one authentic `(body, hmac)` pair can cause the handler to process that body under an arbitrary victim shop domain, i.e., cross-tenant data confusion/injection driven entirely through this gem's trusted `WebhookMetadata.shop` field. This is a High-severity impact per the rubric (identity boundary — shop attribution — is not actually authenticated, only the body bytes are).

### Likelihood Explanation
Likelihood is constrained by the fact that the attacker needs at least one genuine `(body, hmac)` pair signed with the app's real `client_secret` — something they can obtain legitimately if they run their own store using the app (a normal, unprivileged capability, no leaked secrets needed). Given that, forging the `shop`/`topic`/`webhook_id` headers on the replayed request is trivial since the gem does not bind them to the signature at all.

### Recommendation
Include `shop`, `topic`, and `webhook_id` (or at minimum `shop`) in the signed/verifiable string, or independently verify that the `shop` header matches a shop the app has an active session/installation for before invoking the handler, rather than trusting the header value implicitly once the body HMAC passes.

### Proof of Concept
1. App receives (or attacker, as a legitimate merchant of their own store, receives) a genuine webhook POST with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker resends the same `B` and `H` to the app's webhook endpoint but replaces `X-Shopify-Shop-Domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully (headers only need to be present, not verified) — [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `to_signable_string` (`B` only) and succeeds because `H` is valid for `B` — [6](#0-5) .
5. The handler is invoked with `WebhookMetadata.shop == "victim-shop.myshopify.com"` even though the HMAC never certified that shop value — [7](#0-6) .

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
