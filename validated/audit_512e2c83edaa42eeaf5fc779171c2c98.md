### Title
Webhook processing trusts unauthenticated `shop-domain`, `topic`, and other headers not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies only the raw request body against the HMAC signature, but the `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from unauthenticated HTTP headers — are handed to the app's webhook handler as trusted metadata. An attacker who can obtain one genuine, HMAC-signed webhook payload (e.g. by installing the app on their own shop) can replay that body while forging the `x-shopify-shop-domain`/`x-shopify-topic`/`x-shopify-webhook-id` headers, and the gem will report the webhook as validly "from Shopify" for an arbitrary shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The HMAC validator computes and compares the signature solely over this signable string: [2](#0-1) 

Yet `Registry.process` reads `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all sourced from HTTP headers that are never part of the signed payload — and passes them straight into the app's handler as authenticated metadata: [3](#0-2) 

The `shop`, `topic`, `webhook-id`, and `api-version` headers are read directly with no cross-check against the signed body: [4](#0-3) 

This breaks the identity binding: `hmac(raw_body)` valid ⇏ `shop header == shop that generated raw_body`. The gem's own documentation states that `Registry.process` "will verify the request did indeed come from Shopify," implying the whole webhook (including the shop identity) is authenticated, which is not the case: [5](#0-4) 

### Impact Explanation
Any consumer that keys per-tenant behavior off `WebhookMetadata#shop` (e.g., looking up a merchant's session/access token, writing merchant-scoped records, or making an authenticated API call for "that shop" in response to the webhook) can be tricked into acting on a different, victim shop's identity while the actual body content still validates as genuine (since it was authentically signed for the attacker's own shop). This is a cross-tenant identity-binding bypass: the attacker only needs a legitimate app install on any shop (including their own trial/dev store) to obtain a validly-signed body, then can relabel it as belonging to a victim shop by forging headers, since headers are outside the HMAC's scope.

### Likelihood Explanation
Exploitation requires no privileged credentials — only the ability to install the app once on an attacker-controlled shop (or observe a real webhook delivery) and then replay the raw body to the app's public webhook endpoint with modified `x-shopify-shop-domain`/`x-shopify-topic` headers. `Registry.process` performs no cross-shop or cross-topic consistency check, and the documented contract encourages developers to trust `data.shop`/`data.topic` unconditionally.

### Recommendation
Bind the shop (and topic/webhook id) into the signed material, or otherwise cryptographically tie the header values to the verified request — e.g. include the `shop-domain`/`topic`/`webhook-id` headers in `to_signable_string`, or independently verify that the shop asserted in headers is one the gem's own registration/session store expects for this webhook_id before dispatching to the handler. At minimum, update `HmacValidator`/`Webhooks::Request` so that a change to any of these headers invalidates the HMAC.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body and its valid `x-shopify-hmac-sha256` header.
2. Attacker POSTs the identical raw body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally a different `x-shopify-topic`).
3. `HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC: [6](#0-5) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker-controlled body, and acts as though this is a legitimate event for the victim shop.

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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
