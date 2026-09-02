### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw body only, while the `shop` (tenant identity) is read from an unsigned header. `Registry.process` trusts that unsigned `shop` value once the body HMAC checks out, so a valid `(body, hmac)` pair captured from one tenant's legitimate webhook can be replayed with a different `shop-domain` header to make the host app believe the payload belongs to a different, victim shop.

### Finding Description
`Utils::HmacValidator.validate` verifies `request.to_signable_string` against the HMAC using the app's secret [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body` — none of the HTTP headers, including `x-shopify-shop-domain`, are part of the signed material [2](#0-1) . Yet `shop` is read straight from that unsigned header:

```
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [3](#0-2) 

`Registry.process` only checks the HMAC over the body before dispatching to the handler with the (unverified) `shop`:
```
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

The identity binding that should hold is: `HMAC-verified bytes == the bytes the tenant field is derived from`. Here it is instead `HMAC-verified bytes (raw body) != tenant identity (shop-domain header, unsigned)`. Because the two are decoupled, any request whose body+HMAC pair is valid for *some* shop will pass validation regardless of the `shop-domain` header value supplied in that same request.

### Impact Explanation
This is a cross-tenant binding failure delivered through the library's own webhook-processing API surface (`Registry.process` / `Utils::HmacValidator.validate` / `Webhooks::Request`), not something that depends on the host ignoring documented behavior — the library itself hands the handler an unauthenticated `shop` value alongside an authenticated body. A host app that keys per-tenant lookups (session/access-token retrieval, data writes) off `WebhookMetadata#shop` — the exact intended use, per `docs/usage/webhooks.md` and `WebhookMetadata` — can be made to process or act on data under the wrong tenant identity, i.e., cross-tenant access/confusion, which is a Critical-class impact per the stated scope.

### Likelihood Explanation
Any actor who can install the target app on a shop they control (an ordinary, unprivileged merchant signup — no `api_secret_key`, access token, or leaked credential required) can trigger a real webhook delivery for their own shop, capture the resulting `(raw_body, hmac)` pair from the request Shopify sends to the app's public webhook endpoint, and then send an independent HTTP POST to that same public endpoint with the identical body/HMAC but an attacker-chosen `x-shopify-shop-domain` header. `Utils::HmacValidator.validate` will still succeed because headers are excluded from the signable string, so likelihood is high given only a webhook subscription and the ability to send an arbitrary HTTP request to the app's endpoint.

### Recommendation
Bind the shop identity into the HMAC-verified material, or otherwise cryptographically tie `shop` to the signed body:
- Include the `shop-domain` (and other header-derived fields the app trusts) in `to_signable_string` for webhooks, matching what is actually signed by Shopify if it does so, or
- Independently verify `shop` against a value derived from data inside the signed body/topic, or
- Document/require that `Registry.process` callers additionally verify `request.shop` against an already-known, registered shop for the given webhook topic before trusting it, rather than treating the header as authenticated once the HMAC over the body passes.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook event so Shopify POSTs a legitimate `(raw_body, x-shopify-hmac-sha256)` pair to the app's public webhook endpoint.
2. Capture that exact `raw_body` and `x-shopify-hmac-sha256` value (attacker fully controls their own shop's webhook payload content, e.g. via order/product edits).
3. Send a new HTTP POST directly to the same public webhook endpoint URL, reusing the identical raw body and `x-shopify-hmac-sha256` header, but set `x-shopify-shop-domain: victim.myshopify.com` and any desired `x-shopify-topic`/`x-shopify-webhook-id`.
4. `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only [5](#0-4)  — it matches, so `Registry.process` dispatches to the handler with `shop: "victim.myshopify.com"` [6](#0-5) , even though the payload actually originated from the attacker's own shop.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
