### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant event spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating the HMAC over the request body only, then hands the caller-supplied `shop-domain` header to the app's handler unauthenticated, so the "shop that sent this event" is never bound to the value that was actually HMAC-signed.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature over `verifiable_query.to_signable_string`, and for webhook requests that method returns only the raw HTTP body: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed content at all: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler, without re-deriving or checking it against anything cryptographically bound to the signature: [3](#0-2) 

The security-relevant equality the gem is implicitly asserting is:
`hmac_valid(body, secret) == true` implies `shop header == the shop that generated this body`

That equality does not hold: the HMAC only proves "this exact body was signed with our `api_secret_key`" — it says nothing about which header values (`shop-domain`, `topic`, `api-version`, `webhook-id`) accompanied that body. Since `api_secret_key` is shared across every shop installed on a given app (Shopify signs webhooks for all merchants of an app with the same app secret), a byte-identical webhook body/HMAC pair legitimately delivered for one shop remains a valid HMAC for **any** `shop-domain` header value an attacker chooses to attach to a replayed request, because `shop-domain` is never part of the signed bytes.

### Impact Explanation
This is a field-acted-on-but-not-HMAC-bound issue matching the flagged bug class: `request.shop` is used by every downstream handler to route/attribute the event to a tenant (`WebhookMetadata.new(... shop: request.shop ...)`), yet it can be swapped independently of the cryptographic proof. If webhook bodies are ever observable to an attacker (e.g., logged, leaked via error messages, replayed from a previous capture, or simply guessable/duplicable for topics with generic bodies such as `app/uninstalled` or GDPR topics), the attacker can resend that exact body with a different `shop-domain` header and a still-valid HMAC, causing host applications built on this gem to process an event as if it originated from a shop it did not come from — a cross-tenant event/data confusion.

### Likelihood Explanation
Exploitation requires the attacker to obtain a previously-valid `(body, hmac)` pair, which is a real but non-trivial precondition (log exposure, network capture, or a topic whose body is static/predictable). Given that, forging the tenant attribution requires no knowledge of `api_secret_key`, since only the header is changed. This is a design gap in the gem's own webhook-verification API surface (not a host misuse issue), since the gem advertises `Registry.process` as validating the webhook and exposes `shop` as a trusted field on the same `Request` object.

### Recommendation
Include `shop-domain`, `topic`, `api-version`, and `webhook-id` in the signable payload (or otherwise cryptographically bind them, e.g. by hashing them together with the body before comparing against the HMAC) so that `to_signable_string` covers every field the gem exposes as verified/trusted, not just the body.

### Proof of Concept
1. Capture (or otherwise obtain) one legitimate webhook delivery: `raw_body = B`, headers include `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(secret, B)`, and `x-shopify-shop-domain: shop-a.myshopify.com`.
2. Replay a POST to the app's webhook endpoint with the same `raw_body = B` and same `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `B` against `H`: [4](#0-3) 
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "shop-b.myshopify.com", body: parsed(B), ...)`, even though the signature only ever attested to shop-a's payload.

**Uncertainty note:** I was not able to load `lib/shopify_api/webhooks/webhook_handler.rb` in full (only located it via grep) to confirm the exact `WebhookMetadata` field list beyond what is shown in `registry.rb`'s call site; this does not affect the core finding, since the `shop` field being unauthenticated is demonstrated directly in `request.rb` and `hmac_validator.rb`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
