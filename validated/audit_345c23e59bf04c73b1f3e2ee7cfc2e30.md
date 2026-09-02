### Title
Webhook `shop`/`topic`/`webhook_id` headers are not covered by HMAC verification, enabling cross-tenant webhook spoofing via replay - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify," but the HMAC check it performs only covers the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values — all of which come from unauthenticated HTTP headers and are handed directly to the app's business logic — are never part of the signed material. An attacker who can obtain any one genuinely-signed webhook body (e.g. by installing the target app on their own shop) can replay that exact body to the app's webhook endpoint while substituting a different `shop-domain` header, and the request will still pass verification, causing the app to process attacker-supplied data under a victim shop's identity.

### Finding Description
The identity binding that should hold is:
`shop header trusted by the app == shop that actually produced the HMAC-signed payload`

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and the `shop`, `topic`, `webhook_id`, `api_version` accessors are simple, unauthenticated reads of the HTTP headers: [2](#0-1) 

`Registry.process` validates only this body-derived HMAC, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the metadata passed to the app's handler: [3](#0-2) 

Because `HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) and compares it against the `hmac` header: [4](#0-3) 

the header fields are fully decoupled from the cryptographic check. Any attacker who has one valid `(raw_body, hmac)` pair signed with the app's `client_secret` — trivially obtainable by installing the app on their own shop and capturing a real webhook delivery — can resend that same body/HMAC pair with an arbitrary `shopify-shop-domain` (or `x-shopify-shop-domain`) header value. `Registry.process` will accept it as authentic and dispatch it to the app's handler with the attacker-chosen `shop`, breaking the tenant boundary the HMAC is supposed to enforce.

The library's own documentation reinforces that developers are expected to rely on `process` for full authenticity, stating it "will verify the request did indeed come from Shopify": [5](#0-4) 
This is misleading in that it implies the whole request (including which shop it is attributed to) is verified, when only the body bytes are.

### Impact Explanation
This breaks the tenant identity binding between an incoming webhook and the shop it is attributed to. A handler that uses `data.shop` to select which merchant's records to create/update (the documented usage pattern) can be tricked into writing or acting on data under a shop it does not belong to, i.e. cross-tenant access — one of the qualifying Critical impacts.

### Likelihood Explanation
Exploitation requires only: (1) the attacker installs the target app on a shop they control (no special privilege beyond being a normal merchant/app installer), (2) they capture one legitimate webhook delivery (body + HMAC header) sent to their own endpoint, and (3) they replay that exact body/HMAC pair to the app's webhook endpoint with a forged `shop-domain` header. No access token, `client_secret`, or privileged account is required — this fits the "unprivileged internet user" threat model.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material verified by the gem, or, at minimum, stop advertising `process` as validating the full request identity and require/perform an explicit check that `request.shop` matches an app-known, previously authenticated installation before invoking the handler. Concretely:
- Extend `VerifiableQuery`/`HmacValidator` usage for webhooks so the header-derived `shop` (and `topic`/`webhook_id`) are bound into the value being verified, or
- Have `Registry.process` require the caller to supply the expected shop (e.g. resolved from an existing session store) and reject if it doesn't match `request.shop`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw POST, including the `shopify-hmac-sha256` header and body.
2. Replay the identical body and `shopify-hmac-sha256` header to the app's webhook endpoint, but change `shopify-shop-domain` (or `x-shopify-shop-domain`) to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over the unchanged body and matches the unchanged signature — validation succeeds.
4. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., webhook_id: ..., api_version: ...)`, i.e., attacker-controlled body processed under the victim shop's identity.

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
