### Title
Webhook `shop` identity is trusted from an unauthenticated header not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, then hands the handler a `WebhookMetadata` struct whose `shop` field is read straight from the `x-shopify-shop-domain` HTTP header — a value that is never included in the HMAC-signed material. This breaks the intended identity binding `shop_authenticated == shop_the_handler_trusts`, allowing any actor who can obtain one validly-signed webhook body (e.g. by installing the app on their own store) to relabel it as belonging to any other shop.

### Finding Description
`Webhooks::Request#hmac` and `#to_signable_string` show the signed payload is the raw body only: [1](#0-0) 

`shop` is parsed from `shopify_header("shop-domain")`, a header that is not part of `to_signable_string` and therefore is completely outside the HMAC computation: [2](#0-1) [3](#0-2) 

`HmacValidator.validate` only ever checks `verifiable_query.hmac` against `verifiable_query.to_signable_string` (the body), never any header value: [4](#0-3) 

`Registry.process` uses this HMAC check as the *sole* authentication gate, and then forwards `request.shop` — the unauthenticated header — directly into `WebhookMetadata`, which is the value host applications use to look up/attribute the tenant the webhook belongs to: [5](#0-4) [6](#0-5) 

The `client_secret` used to compute the webhook HMAC is an **app-level** credential shared across every shop that installs the app — it is not shop-specific. This means an unprivileged user who installs the app on their own (attacker-controlled) development store can legitimately receive real, correctly-signed webhook deliveries from Shopify. Because the signature covers only the JSON body and not the `x-shopify-shop-domain` header, the attacker can capture such a delivery and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still pass (the body is untouched and was signed with the correct, shared `client_secret`), so `Registry.process` will invoke the handler with `WebhookMetadata#shop` claiming to be the victim shop while the actual body content is attacker-controlled.

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the equality the code implicitly assumes — `hmac_verified_body → shop_header_is_authentic` — does not hold, because `shop` was never part of what was signed.

### Impact Explanation
Any downstream application built on this gem that trusts `WebhookMetadata#shop` (which is the documented/intended way to route webhook data per tenant, matching values against stored `ShopifyAPI::Auth::Session` records) can be made to associate attacker-supplied webhook payloads with an arbitrary victim shop. Depending on the handler logic this enables cross-tenant data injection/confusion (e.g. writing forged order/customer/fulfillment data under a victim's shop record, or forging mandatory compliance webhooks like `customers/redact` against a shop the attacker doesn't own), which the rules classify as cross-tenant access — a Critical-impact class.

### Likelihood Explanation
The prerequisite — installing the target app on a store the attacker controls (e.g. a free Shopify Partner development store) — is realistic for any public or semi-public Shopify app and requires no privileged access, leaked secrets, or social engineering. Capturing one's own legitimately delivered webhook and re-POSTing it with a modified header is trivial once the endpoint is known (endpoints are typically documented in the app's manifest/config and are public HTTP(S) URLs by design).

### Recommendation
Bind the `shop` value into the material that is authenticated, or independently authenticate it:
1. Require the `shop` (and ideally `topic`/`webhook_id`) to be included in `to_signable_string` so it is covered by the HMAC, or
2. Cross-check `request.shop` against a shop the app has a stored, previously-authenticated `Session`/access token for before processing, rejecting webhooks for shops the app doesn't recognize as installed, and
3. Document clearly that `WebhookMetadata#shop` is not itself an authenticated value and must not be used as a sole tenant-selection key without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own dev store `attacker.myshopify.com`, obtaining legitimate webhook deliveries signed with the app's (shared) `client_secret`.
2. Attacker captures one such delivery, e.g. an `orders/create` webhook:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-signature-over-body>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: ...
   Body: {"id": 1, ...attacker-controlled order data...}
   ```
3. Attacker resends the identical request but rewrites only the header:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
   The body (and thus the HMAC) is unchanged, so `Utils::HmacValidator.validate` at `lib/shopify_api/webhooks/registry.rb:190` still returns `true`.
4. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "victim.myshopify.com"` and invokes the app's handler, which now processes attacker-controlled data attributed to the victim tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L66-70)
```ruby

      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
