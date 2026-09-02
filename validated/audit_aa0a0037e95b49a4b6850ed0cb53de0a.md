### Title
Webhook shop-domain identity spoofing due to HMAC covering only the raw body, not the tenant-identifying header - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate(request)` [1](#0-0) . The `shop` (tenant identity), `topic`, `webhook_id`, and `api_version` values used to build the `WebhookMetadata` passed to the app's handler are read directly from unauthenticated HTTP headers and are never included in the signed payload [2](#0-1) .

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [3](#0-2) , and `HmacValidator.validate_signature` computes/compares the HMAC exclusively against that signable string [4](#0-3) . Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are parsed straight from the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers with no cryptographic binding to the body or to each other [5](#0-4) .

`Registry.process` uses the *unverified* `shop` value to construct the `WebhookMetadata` object dispatched to the app's business-logic handler: [6](#0-5) 

This breaks the identity binding that should hold: `HMAC-verified bytes == bytes the tenant identity is derived from`. In this implementation, `HMAC-verified bytes (raw_body) != bytes used to select the tenant (shop header)`. Any request whose body+HMAC pair is a legitimately Shopify-signed pair (e.g. a webhook the attacker's own shop legitimately triggered by taking an action that produces a webhook with attacker-controlled/predictable body content, such as `orders/create` or `app/uninstalled`) will pass `HmacValidator.validate` even if the `x-shopify-shop-domain` header is swapped to name a different, victim shop — because that header is not part of what is signed.

### Impact Explanation
This is a cross-tenant identity-binding violation: the value that authorizes the request (HMAC over body) is disjoint from the value that determines which tenant's data/state the handler acts on (`shop` header). A single app installation serves many merchants under one shared `api_secret_key`; any one of those merchants can generate a validly-HMAC-signed `(raw_body, hmac)` pair for their own shop and then use it to have the app process that payload *as if it originated from another shop*, since `process` never checks that the `shop` header matches the shop the body/HMAC pair was actually generated for. Depending on what the app's registered webhook handler does with `data.shop` (e.g., updating billing state, marking installation status, mutating per-shop records keyed by `data.shop`, or reacting to `app/uninstalled`/`shop/redact` to purge or disable another tenant's data), this enables cross-tenant data corruption or a tenant being forced into another tenant's state — a Critical, cross-tenant access class issue per the given impact taxonomy.

### Likelihood Explanation
Exploitation requires the attacker to control (or install) at least one shop that uses the same app so they can obtain one legitimately Shopify-signed webhook body/HMAC pair, and to know/guess the target victim's `myshopify.com` domain (which is often discoverable or guessable). No access token, `api_secret_key`, or privileged account is required — this is reachable by any user who can install the app on their own store, which the gem/app itself normally allows. The webhook endpoint is a standard public HTTP endpoint documented for host apps to expose [7](#0-6) , so likelihood is realistic though it depends on the host handler actually keying sensitive per-shop mutation logic off `data.shop` without a secondary sanity check (e.g., confirming the shop has an active session/is a known installed tenant).

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the HMAC-verified surface, or otherwise cryptographically/logically bind them before dispatch:
- Preferably, include the `shop`, `topic`, and `webhook_id` header values in `to_signable_string` alongside the raw body so `HmacValidator` fails closed if any of them are altered relative to what Shopify actually sent for that specific payload; or
- At minimum, require `Registry.process` to verify that `request.shop` corresponds to a shop with an existing, currently-installed session before invoking the handler, rejecting webhooks for shops the app doesn't recognize as installed for that specific webhook subscription id.
- Document to implementers that `webhook_id`/`shop` are not part of the signed payload today, so they should not be trusted for authorization decisions without additional verification (e.g., looking up the specific webhook subscription id against Shopify's Admin API per shop).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers an event that fires a subscribed webhook topic (e.g. `orders/create`) with a body they can predict/control (order fields), or captures the raw body Shopify sends along with the valid `X-Shopify-Hmac-Sha256` value.
2. Attacker replays this exact `(raw_body, hmac)` pair to the app's public webhook endpoint but replaces the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers and body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(raw_body)` against `api_secret_key` [8](#0-7)  — this passes because the body/HMAC pair is genuinely valid for that secret.
4. `Registry.process` builds `WebhookMetadata` with `shop: request.shop` = `"victim-shop.myshopify.com"` (attacker-supplied header) [9](#0-8)  and dispatches it to the host app's handler, which now performs actions attributed to `victim-shop.myshopify.com` using attacker-controlled body content.

Note: I could not find any additional check elsewhere in `lib/shopify_api/**` (outside `rest/resources`) that cross-validates the `shop` header against the specific webhook subscription or an active session before handler dispatch; this is based on the full `Registry`/`Request`/`HmacValidator` code paths reviewed above.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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

**File:** docs/usage/webhooks.md (L123-136)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
```
