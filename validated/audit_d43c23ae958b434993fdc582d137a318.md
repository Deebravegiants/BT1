## Title
Webhook `shop-domain` (and topic/webhook-id) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body [1](#0-0) , so `HmacValidator.validate` authenticates *only the body bytes* against the app's shared `client_secret` [2](#0-1) . The `shop` identity used downstream is taken straight from the `X-Shopify-Shop-Domain` header, which is never part of the signed material [3](#0-2) . `Registry.process` trusts this unauthenticated header to attribute the event to a shop when invoking the handler [4](#0-3) .

### Finding Description
The identity binding that should hold is:

`shop attributed to the webhook == shop whose secret actually signed the payload`

Instead, the gem only verifies:

`HMAC(raw_body, shared client_secret) == received HMAC`

and separately, unauthenticated, reads:

`shop = header("shop-domain")`

Because a single app has one `client_secret` shared across *every* shop that installs it, any unprivileged party can install the app on their own store (a normal, unprivileged onboarding action) and receive a legitimately-signed webhook body from Shopify for that store. Since the signature covers only `@raw_body` and not the shop-domain/topic/webhook-id headers, that exact request (body + valid HMAC) can be replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to any victim shop's domain. `HmacValidator.validate` recomputes the HMAC over the same raw body with the same shared secret and returns `true`, and `Registry.process` then calls the handler with `shop: request.shop` set to the attacker-chosen victim domain [5](#0-4) . This is confirmed by the test setup, which signs only `"{}"` and sets `shop-domain` independently: [6](#0-5) .

Nothing in `Request` or `Registry` cross-checks that the header-supplied shop is bound to the signed content, nor that it corresponds to a shop actually known to have installed the app.

### Impact Explanation
This breaks tenant isolation: an application built on this gem that dispatches business logic keyed by `WebhookMetadata#shop` (e.g., updating records, revoking access, crediting/debiting balances, syncing inventory) can be made to act on behalf of, or against, a shop the attacker does not control, using only a payload the attacker legitimately received for their own (attacker-owned) shop. This is a cross-tenant access vulnerability with no requirement on `api_secret_key`, access tokens, or victim credentials — matching the "Critical: cross-tenant access" category.

### Likelihood Explanation
Likelihood is high: the only prerequisite is installing the target app on an attacker-controlled shop (a normal, unprivileged action available to anyone) and capturing one webhook delivery. No cryptographic secret, brute force, or privileged access is required — only a header rewrite on replay.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signed material used by `to_signable_string`, or otherwise cryptographically bind the shop identity to the signature (e.g. verify the shop against a stored, previously-established session/installation record before dispatching to a handler), rather than trusting the unauthenticated `X-Shopify-Shop-Domain` header value returned by `Request#shop`.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; wait for/trigger a webhook delivery, capturing:
   - body: `{}` (or any real payload)
   - header `X-Shopify-Hmac-Sha256`: `H = HMAC-SHA256(client_secret, body)`
   - header `X-Shopify-Shop-Domain`: `attacker.myshopify.com`
2. Resend the identical HTTP request to the app's webhook endpoint, but change only `X-Shopify-Shop-Domain` to `victim.myshopify.com` (keep body and `X-Shopify-Hmac-Sha256` unchanged).
3. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, body)` — unchanged from step 1 — and returns `true` [7](#0-6) .
4. The handler is invoked with `shop: "victim.myshopify.com"` [8](#0-7) , causing the host application to process attacker-controlled data as if it were an authentic event from the victim shop.

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

**File:** test/webhooks/registry_test.rb (L16-30)
```ruby
        hmac = OpenSSL::HMAC.digest(
          OpenSSL::Digest.new("sha256"),
          ShopifyAPI::Context.api_secret_key,
          "{}",
        )

        @headers = {
          "x-shopify-topic" => @topic,
          "x-shopify-hmac-sha256" => Base64.encode64(hmac),
          "x-shopify-shop-domain" => @shop,
          "x-shopify-webhook-id" => "b1234-eefd-4c9e-9520-049845a02082",
          "x-shopify-api-version" => "2024-01",
        }

        @webhook_request = ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: @headers)
```
