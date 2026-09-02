### Title
Webhook tenant identity (`shop`, `topic`, `webhook-id`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body when validating a webhook's HMAC, while the `shop`, `topic`, and `webhook_id` values — which are used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the event to a tenant — are read directly from unauthenticated HTTP headers. This breaks the intended binding `signed_body == HMAC_verified_content` versus `shop_used_for_tenant_attribution == header_value`, letting anyone who can produce one valid app-level HMAC (e.g. by installing the public app on their own store) replay that same body/HMAC pair with a forged `shop`/`topic` header to make the app process an event as if it came from a different, unrelated merchant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`hmac`, `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers, none of which are covered by that signable string: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e. the body) against the app's `api_secret_key`: [3](#0-2) 

`Registry.process` validates only this HMAC, then immediately trusts `request.topic` and `request.shop` (unauthenticated headers) to route to a handler and build the `WebhookMetadata` the app's business logic acts on: [4](#0-3) 

Because `api_secret_key` is the app's single client secret shared across every merchant that installs the app (not a per-shop secret), any merchant who installs the app can obtain a body+HMAC pair that Shopify signed for their own shop's genuine event. That same body/HMAC pair remains valid if it is replayed with the `shop-domain`, `topic`, or `webhook-id` headers swapped to arbitrary values, since none of those fields are part of the signed content. The equality the code implicitly assumes — "the shop whose HMAC was verified" == "the shop attributed to this event" — does not actually hold, because the second value is taken from an input channel (`headers`) the HMAC never covers.

### Impact Explanation
An app that uses `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) to key persistence, trigger per-tenant side effects, or make authorization decisions (a documented and expected usage pattern for this gem) can be made to attribute a webhook event to the wrong merchant. This is a cross-tenant integrity issue: data intended for shop A can be written/processed under shop B's identity, or a handler gated on `topic` (e.g. mandatory compliance topics like `customers/redact`) can be invoked with a forged topic for an arbitrary shop. This falls under "cross-tenant access" impact.

### Likelihood Explanation
Likelihood is bounded by the fact that the attacker needs at least one valid signed (body, HMAC) pair, which requires the app to be installed on a shop the attacker controls — trivial for any public Shopify app, since installing on a free development store requires no privileged access to the target. Once obtained, forging the header values is a pure HTTP replay with no cryptographic material required, making this a straightforward, repeatable exploit and not merely theoretical.

### Recommendation
Bind the identity-critical headers into the HMAC input, or otherwise authenticate them independently of the body — for example, include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or require the caller to separately verify `shop` against the session/store the webhook is expected to originate from before trusting `request.shop`/`request.topic` for routing or persistence.

### Proof of Concept
1. Install the target Shopify app (any public app is installable by any store owner) on an attacker-controlled development store `attacker-shop.myshopify.com`.
2. Trigger a webhook event on the attacker's own shop (e.g. `orders/create`) and capture the raw POST: body `B`, and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(api_secret_key, B)`, and `api_secret_key` is shared across all installs of the app).
3. Replay the exact same body `B` and header `H` to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `Utils::HmacValidator.validate` (verifying only `B` against `H`) still passes per [3](#0-2) , and `Registry.process` dispatches the handler with `WebhookMetadata` built from the forged `shop`/`topic` headers per [5](#0-4) , causing the app to process attacker-supplied data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
