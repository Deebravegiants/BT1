### Title
Webhook Shop-Domain Spoofing via HMAC Signature Not Covering Identity Headers - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook using an HMAC that is computed only over the raw request body, then hands the caller-supplied, unauthenticated `shopify-shop-domain` header value to the app as the trusted tenant identifier. Because the signature never binds the shop (or topic) header to the signed bytes, a party who receives one genuine signed webhook for their own shop can replay that exact body with a substituted `shop-domain` header and have it accepted as an event for a different, victim shop.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes and compares the HMAC solely against that signable string: [2](#0-1) 

`Request#shop` (and `#topic`, `#webhook_id`) are read straight from HTTP headers, which are not part of the signed payload at all: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed to the app's handler, with no cross-check that this shop is the one the signed body actually belongs to: [4](#0-3) 

The identity binding that should hold is:
`shop authenticated by the signature == shop delivered to the application handler`

Because the HMAC only covers the body bytes, this equality is never enforced — `hmac_valid(body)` says nothing about which shop the body is "for." Any party who has received one legitimately-signed webhook for their own store (trivial: install the app, wait for any webhook) possesses a `(raw_body, valid_hmac)` pair signed with the app's shared `client_secret`. They can resend that exact body to the app's webhook endpoint with the `shopify-shop-domain` header changed to an arbitrary victim shop (and `shopify-topic` changed to any registered topic); `HmacValidator.validate` still passes because it re-hashes the same untouched body, and `Registry.process` dispatches the handler with `shop: request.shop` set to the attacker-chosen victim domain.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: an app cannot trust `WebhookMetadata#shop` as proof the event originated from that merchant. Applications typically key data storage, deduplication, or authorization decisions off the webhook's `shop` field, so an attacker (any merchant capable of installing the app) can inject spoofed events attributed to a different, unrelated tenant — a cross-tenant access vector, without ever needing the app's `client_secret`, an access token, or any credential belonging to the victim.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even low-privilege) installer of the target app on their own store — no secrets, tokens, or victim cooperation are needed. Capturing one authentic `(body, hmac)` pair and replaying it with a modified `shop-domain`/`topic` header is trivial for anyone who can send arbitrary HTTP requests to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and topic) inside the signed material, or otherwise cryptographically bind them to the payload before dispatching to handlers (e.g., compute/verify the HMAC over `shop + topic + body`, or require applications to reconcile `request.shop` against a authoritative registered-shop list before using it as an identity). At minimum, `Registry.process` should not treat `request.shop` as trusted solely because the body-only HMAC validated.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook (e.g., `orders/create`), capturing the raw POST: body `B`, and headers including a valid `x-shopify-hmac-sha256` computed over `B`.
2. Attacker resends the identical body `B` and identical valid HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally changes `x-shopify-topic`).
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `B` only — it matches, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) proceeds.
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
