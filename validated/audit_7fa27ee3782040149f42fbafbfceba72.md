## Title
Webhook shop-domain spoofing via unsigned header — HMAC covers only the raw body, not the `shop`/`topic`/`webhook_id` identity fields ([File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`])

### Summary
`ShopifyAPI::Webhooks::Registry.process` claims to "verify the request did indeed come from Shopify," but the cryptographic check only binds the raw request body to the app's secret. The `shop` value that the gem hands to the application's webhook handler as the tenant identifier is read straight from an HTTP header that is never included in the HMAC computation, so it can be swapped independently of the signature — the exact "bytes verified vs. bytes/identity acted on" mismatch pattern in the source report (there, `txid` argument vs. parsed `tx_hash`; here, signed body vs. unsigned `shop` header).

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled independently from HTTP headers that are not part of that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` then trusts `request.shop` unconditionally to build the `WebhookMetadata` passed to the app's handler, right after the HMAC check that never touched that field: [4](#0-3) 

The documented contract explicitly says `process` "will verify the request did indeed come from Shopify" and that `data.shop` is "the shop domain of the webhook": [5](#0-4) [6](#0-5) 

**Binding that should hold:** `shop_header == shop_that_the_HMAC_actually_authenticates`.
**Reality:** the HMAC authenticates only `raw_body`; `shop_header` is unauthenticated and independently substitutable. Since a single `api_secret_key` per app is shared across every shop that installs the app, any merchant (an "unprivileged" actor with respect to other tenants) can capture a genuinely-signed webhook delivered to their own shop, then replay the identical body/HMAC/topic while swapping only the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to point at a victim shop. `HmacValidator.validate` still returns `true` because it never inspects that header, and `Registry.process` forwards `WebhookMetadata.new(shop: request.shop, ...)` to the handler as if Shopify had asserted that binding.

### Impact Explanation
This is a cross-tenant identity-confusion vulnerability at the gem layer: the library asserts a shop→payload binding it did not actually verify. Any application that uses `data.shop` from the documented `WebhookMetadata` object (as the shipped example handler does — `shop_domain: data.shop`) to key persistence, authorization, or side effects can be made to apply attacker-supplied webhook content to a different tenant's account, meeting the "cross-tenant access" bar.

### Likelihood Explanation
Medium: it requires an attacker who already has a working installation of the target app on any shop (a normal merchant, not a privileged actor), who can capture one of their own real webhook deliveries and replay it with an edited header to the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or TLS interception is needed — only network access to the same webhook URL every legitimate delivery already targets.

### Recommendation
Bind the identity headers into the signed material verified by `Utils::HmacValidator`, or explicitly document/require that `Registry.process`/`WebhookMetadata.shop` must never be trusted for tenant identity without the caller separately re-validating it against their own shop/session records (and update the "will verify the request did indeed come from Shopify" doc wording, which currently implies full authentication of `shop`). At minimum, gate `WebhookMetadata.shop` in `Registry.process` behind a check that `request.shop` matches a shop known to have this specific `webhook_id`/topic registered.

### Proof of Concept
1. Register the app on attacker-controlled shop `attacker.myshopify.com`; capture a genuine webhook delivery: body `B`, headers including `x-shopify-hmac-sha256: H(B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Replay the identical HTTP POST to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim.myshopify.com` (body and HMAC header untouched).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` — still matches, since `to_signable_string` never included the shop header.
4. `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)` is delivered to the app's handler, which processes attacker-controlled content under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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

**File:** docs/usage/webhooks.md (L10-17)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
